####################(Python 3.5)###########################
from pylab import *
import numpy as np
from numpy.ctypeslib import ndpointer, load_library
from ctypes import *
from scipy.special import j0
import sys

interpolation='nearest'
#interpolation='gaussian'
#interpolation=None

### === C library interface ===
libcd = load_library("libsky", ".")
#libcd.sky.restype = None
libcd.sky.restype = c_double
libcd.sky.argtypes = [c_int, c_int, ndpointer(dtype=np.float64, ndim=4, flags='C_CONTIGUOUS'), c_int, c_int, c_int, c_double, c_double,
	c_double, c_double, c_double, c_double, c_double, c_double, c_double]

### === Python ===

tmax=300

dt=0.02

K=0.
dmi=0.18
bapp=0.015
alpha0=0.2
beta0=0.
jx=0.
jy=0.

#AFM = True ### Nx, Ny should be even - Provavelmente AFM = Antiferromagnético
AFM=False

### skyrmion lattice 
gammavalue = 0.
Nx=3
Ny=3

dtout=20
countout=round(dtout/dt)
normcount=1

try:
    initialized
except NameError:
    Nframes=round(tmax/dtout)+1
    initialized = True
    
J0value = j0(gammavalue);

mag = np.zeros((Nx+2,Ny+2,3),np.float64) ### including virtual nodes
magphys = mag[1:Nx+1,1:Ny+1,:] ### physical nodes

dwind=30

i0=int(Nx/2)
j0=int(Ny/2)
irange = np.arange(Nx)
jrange = np.arange(Ny)

xT, yT = np.meshgrid(irange-i0, jrange-j0)
x=xT.T
y=yT.T
r=np.sqrt(x*x+y*y)+1.e-5

r0=10.
def prof(r):
	return (r/r0)*np.exp(-(r-r0)/r0)

def create_skyrmion():
    magphys[:,:,0] = -prof(r)*x/r
    magphys[:,:,1] = -prof(r)*y/r
    magphys[:,:,2] = np.sqrt(1.-magphys[:,:,0]*magphys[:,:,0]-magphys[:,:,1]*magphys[:,:,1])
    inds=np.where(r<r0)
    magphys[inds[0],inds[1],2] = -magphys[inds[0],inds[1],2]

def align_up():
    magphys[:,:,0]=0.
    magphys[:,:,1]=0.
    magphys[:,:,2]=1.


def stripes():
    nperiods=3
    ks=2.*np.pi*nperiods/Nx
    magphys[:,:,0] = np.cos(ks*x+np.pi/2.)
    magphys[:,:,1] = 0.
    magphys[:,:,2] = -np.sin(ks*x+np.pi/2.)

def invstripes():
    nperiods=3
    ks=2.*np.pi*nperiods/Nx
    magphys[:,:,0] = -np.cos(ks*x+np.pi/2.)
    magphys[:,:,1] = 0.
    magphys[:,:,2] = -np.sin(ks*x+np.pi/2.)

def ini_rand():
    magphys[:,:,0] = np.sqrt(2.)*(np.random.rand(Nx,Ny)-0.5)
    magphys[:,:,1] = np.sqrt(2.)*(np.random.rand(Nx,Ny)-0.5)
    magphys[:,:,2] = np.sqrt(2.)*(np.random.rand(Nx,Ny)-0.5)

def ini_rand2():
    for i in range(Nx):
        for j in range(Ny):
            magx = i + 1
            magy = j + 1
            magz = magx + magy
            
            spin = [magx, magy, magz]

            spin[0] = magx / np.sqrt(magx**2 + magy**2 + magz**2)
            spin[1] = magy / np.sqrt(magx**2 + magy**2 + magz**2)
            spin[2] = magz / np.sqrt(magx**2 + magy**2 + magz**2)

            magphys[i][j] = spin
    
ks = 0.18
def one_stripe():
    magphys[:,:,0] = 0.
    magphys[:,:,1] = 0.
    magphys[:,:,2] = 1.
    inds = np.where((x[:,0]>-np.pi/ks)&(x[:,0]<np.pi/ks))
    magphys[inds,:,0] = -np.sin(ks*x[inds,:])
    magphys[inds,:,1] = 0.
    magphys[inds,:,2] = -np.cos(ks*x[inds,:])
    

def one_sk(r,r0):
    magphys[:,:,0] = prof(r)*x/r
    magphys[:,:,1] = prof(r)*y/r
    magphys[:,:,2] = np.sqrt(1.-magphys[:,:,0]*magphys[:,:,0]-magphys[:,:,1]*magphys[:,:,1])
    inds=np.where(r<r0)
    magphys[inds[0],inds[1],2] = -magphys[inds[0],inds[1],2]
   
   
nxcells=3
k0=np.pi*nxcells/Nx
ynew=y/np.sqrt(3.)
def sk_lattice():
    magphys[:,:,0] = -np.cos(k0*2.*ynew)*np.sin(2.*k0*x)
    magphys[:,:,1] = -( np.cos(k0*2.*ynew)*np.sin(2.*k0*ynew) + 2.*np.sin(k0*2.*ynew)*np.cos(k0*(x-ynew))*np.cos(k0*(x+ynew)) )/np.sqrt(3.)
    magphys[:,:,2] = 2*(0.5-np.cos(k0*2.*ynew)*np.cos(k0*(x-ynew))*np.cos(k0*(x+ynew)))

nxcells=1
k0=np.pi*nxcells/Nx
ynew=y/np.sqrt(3.)
def sk_lattice_inverse():
    magphys[:,:,0] = np.cos(k0*2.*ynew)*np.sin(2.*k0*x)
    magphys[:,:,1] = ( np.cos(k0*2.*ynew)*np.sin(2.*k0*ynew) + 2.*np.sin(k0*2.*ynew)*np.cos(k0*(x-ynew))*np.cos(k0*(x+ynew)) )/np.sqrt(3.)
    magphys[:,:,2] = 2*(0.5-np.cos(k0*2.*ynew)*np.cos(k0*(x-ynew))*np.cos(k0*(x+ynew)))

    
ks = dmi
def helix_lattice():
    magphys[:,:,0] = -np.sin(ks*x)
    magphys[:,:,1] = 0.
    magphys[:,:,2] = -np.cos(ks*x)


def create_dwall_x():
    magphys[:dwind,:,0] = 1.
    magphys[dwind:,:,0] = -1.    
    magphys[:,:,1] = 0.
    magphys[:,:,2] = 0.
    
def create_dwall_y():
    magphys[:,:,0] = 0.
    magphys[:dwind,:,1] = 1.
    magphys[dwind:,:,1] = -1.    
    magphys[:,:,2] = 0.

def create_dwall_z():
    magphys[:,:,0] = 0.
    magphys[:,:,1] = 0.
    magphys[:dwind,:,2] = 1.
    magphys[dwind:,:,2] = -1.

def create_dwall_inplane():
    magphys[:,:,0] = 1./np.cosh(0.1*x)
    magphys[:,:,1] = -np.tanh(0.1*x)    
    magphys[:,:,2] = 0.
                   
ini_rand()

mag[0,1:Ny+1,:]=magphys[1,:,:]
mag[Nx+1,1:Ny+1,:]=magphys[Nx-1,:,:]
mag[1:Nx+1,0,:]=magphys[:,1,:]
mag[1:Nx+1,Ny+1,:]=magphys[:,Ny-1,:]

mag[0,0,:]=0.
mag[0,Ny+1,:]=0.
mag[Nx+1,0,:]=0.
mag[Nx+1,Ny+1,:]=0.

### Display initial state
#mx = magphys[:,:,0]
#my = magphys[:,:,1]
#mz = magphys[:,:,2]
#exec(open('display.py').read())

### Transformation to AFM
if(AFM):
    mag[0::2,1::2] *= -1
    mag[1::2,0::2] *= -1

magdata=np.empty((Nframes,Nx+2,Ny+2,3),dtype=np.float64)
magdata[0]=np.copy(mag)
print(magdata[0])

### Run simulation
Edensity = libcd.sky(Nx,Ny,magdata,Nframes,countout,normcount,dt,bapp,dmi,alpha0,beta0,K,jx,jy,J0value)

if(AFM):
    Ebackground = - 2. - K
else:    
    Ebackground = - 2. - K - bapp    
reldensity = Edensity - Ebackground
print('Relative energy density (x1000): %.6f' % (1000*reldensity))    
            
mag = np.copy(magdata[-1])

print(magdata)

# def magsave(filename):
#     savetxt(filename,magdata[-1].ravel(),fmt='%11.8f')
#     print('#\n# Last frame saved to file '+filename)

#np.savez('mag0',mag0=magdata[-1])
#magsave("ic-switch-sk.dat")
#magsave("ic.dat")
#magsave("ic-switch-stripe.dat")

LLG_initialized = True
