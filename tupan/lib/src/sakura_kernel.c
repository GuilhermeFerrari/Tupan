#include "sakura_kernel_common.h"


void
sakura_kernel(
    uint_t const ni,
    real_t const __im[restrict],
    real_t const __irx[restrict],
    real_t const __iry[restrict],
    real_t const __irz[restrict],
    real_t const __ie2[restrict],
    real_t const __ivx[restrict],
    real_t const __ivy[restrict],
    real_t const __ivz[restrict],
    uint_t const nj,
    real_t const __jm[restrict],
    real_t const __jrx[restrict],
    real_t const __jry[restrict],
    real_t const __jrz[restrict],
    real_t const __je2[restrict],
    real_t const __jvx[restrict],
    real_t const __jvy[restrict],
    real_t const __jvz[restrict],
    real_t const dt,
    int_t const flag,
    real_t __idrx[restrict],
    real_t __idry[restrict],
    real_t __idrz[restrict],
    real_t __idvx[restrict],
    real_t __idvy[restrict],
    real_t __idvz[restrict])
{
    for (uint_t i = 0; i < ni; ++i) {
        real_t im = __im[i];
        real_t irx = __irx[i];
        real_t iry = __iry[i];
        real_t irz = __irz[i];
        real_t ie2 = __ie2[i];
        real_t ivx = __ivx[i];
        real_t ivy = __ivy[i];
        real_t ivz = __ivz[i];
        real_t idrx = 0;
        real_t idry = 0;
        real_t idrz = 0;
        real_t idvx = 0;
        real_t idvy = 0;
        real_t idvz = 0;

        for (uint_t j = 0; j < nj; ++j) {
            real_t jm = __jm[j];
            real_t jrx = __jrx[j];
            real_t jry = __jry[j];
            real_t jrz = __jrz[j];
            real_t je2 = __je2[j];
            real_t jvx = __jvx[j];
            real_t jvy = __jvy[j];
            real_t jvz = __jvz[j];
            sakura_kernel_core(
                dt, flag,
                im, irx, iry, irz, ie2, ivx, ivy, ivz,
                jm, jrx, jry, jrz, je2, jvx, jvy, jvz,
                &idrx, &idry, &idrz, &idvx, &idvy, &idvz);
        }

        __idrx[i] = idrx;
        __idry[i] = idry;
        __idrz[i] = idrz;
        __idvx[i] = idvx;
        __idvy[i] = idvy;
        __idvz[i] = idvz;
    }
}

