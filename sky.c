#include <stdio.h>
#include <stdlib.h> // malloc
#include <math.h> // sqrt
#include <string.h> // memcpy
#include <stdbool.h> // boolean datatype
#include <time.h> // timing
#include <omp.h>
//#include <ctype.h> // character handling for getopt routine
//#include <unistd.h> // getopt routine
#include "LLGsolver.h"

double sky(int Nx, int Ny, double *magdata, int Nframes, int countout, int normcount, double dt, 
	double bapp, double dmi, double alpha, double beta, double K, double jx, double jy, double J0value) {
    
    LLG_ini(Nx, Ny, bapp, dmi, alpha, beta, K, jx, jy, J0value);

    double *mag_new = malloc(LLG_dim * sizeof(double));
    double *mag = malloc(LLG_dim * sizeof(double));
    
    memcpy(mag, magdata, LLG_dim * sizeof(double));
    
    int count, frame;
    double t;

    normalize(mag);

    // Start timer
    double t0=omp_get_wtime();
    clock_t c0 = clock();

    for(t=0.,count=0,frame=0;frame<Nframes;count++) {
        
        periodic_bc(mag);
        
        if(count%countout==0) {
            printf("# frame=%d: t=%.3f\n",frame,t);
            memcpy(magdata + frame*LLG_dim, mag, LLG_dim*sizeof(double));
            frame++;
        }

        LLG_evolve(mag, mag_new, dt);
        
        // Normalization
        if(count%normcount==0)
            normalize(mag_new);

        // Update variables
        memcpy(mag,mag_new,LLG_dim*sizeof(double));
        t += dt;
    }

    // Stop timer
    double t1=omp_get_wtime();
    clock_t c1 = clock();

    periodic_bc(mag);
    double Henergy;
    Henergy = magenergy(mag);

    free(mag);
    free(mag_new);
    return Henergy/(Nx*Ny);
}

