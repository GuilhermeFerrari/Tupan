#include "nreg_kernels_common.h"


__attribute__((reqd_work_group_size(LSIZE, 1, 1)))
kernel void
nreg_Xkernel(
    uint_t const ni,
    global real_tn const __im[restrict],
    global real_tn const __irx[restrict],
    global real_tn const __iry[restrict],
    global real_tn const __irz[restrict],
    global real_tn const __ie2[restrict],
    global real_tn const __ivx[restrict],
    global real_tn const __ivy[restrict],
    global real_tn const __ivz[restrict],
    uint_t const nj,
    global real_t const __jm[restrict],
    global real_t const __jrx[restrict],
    global real_t const __jry[restrict],
    global real_t const __jrz[restrict],
    global real_t const __je2[restrict],
    global real_t const __jvx[restrict],
    global real_t const __jvy[restrict],
    global real_t const __jvz[restrict],
    real_t const dt,
    global real_tn __idrx[restrict],
    global real_tn __idry[restrict],
    global real_tn __idrz[restrict],
    global real_tn __iax[restrict],
    global real_tn __iay[restrict],
    global real_tn __iaz[restrict],
    global real_tn __iu[restrict])
{
    uint_t lid = get_local_id(0);
    uint_t gid = get_global_id(0);
    gid = (gid < ni) ? (gid):(0);

    real_tn im = __im[gid];
    real_tn irx = __irx[gid];
    real_tn iry = __iry[gid];
    real_tn irz = __irz[gid];
    real_tn ie2 = __ie2[gid];
    real_tn ivx = __ivx[gid];
    real_tn ivy = __ivy[gid];
    real_tn ivz = __ivz[gid];

    real_tn idrx = (real_tn)(0);
    real_tn idry = (real_tn)(0);
    real_tn idrz = (real_tn)(0);
    real_tn iax = (real_tn)(0);
    real_tn iay = (real_tn)(0);
    real_tn iaz = (real_tn)(0);
    real_tn iu = (real_tn)(0);

    uint_t j = 0;

    #ifdef FAST_LOCAL_MEM
    local real_t _jm[LSIZE];
    local real_t _jrx[LSIZE];
    local real_t _jry[LSIZE];
    local real_t _jrz[LSIZE];
    local real_t _je2[LSIZE];
    local real_t _jvx[LSIZE];
    local real_t _jvy[LSIZE];
    local real_t _jvz[LSIZE];
    for (; (j + LSIZE - 1) < nj; j += LSIZE) {
        real_t jm = __jm[j + lid];
        real_t jrx = __jrx[j + lid];
        real_t jry = __jry[j + lid];
        real_t jrz = __jrz[j + lid];
        real_t je2 = __je2[j + lid];
        real_t jvx = __jvx[j + lid];
        real_t jvy = __jvy[j + lid];
        real_t jvz = __jvz[j + lid];
        barrier(CLK_LOCAL_MEM_FENCE);
        _jm[lid] = jm;
        _jrx[lid] = jrx;
        _jry[lid] = jry;
        _jrz[lid] = jrz;
        _je2[lid] = je2;
        _jvx[lid] = jvx;
        _jvy[lid] = jvy;
        _jvz[lid] = jvz;
        barrier(CLK_LOCAL_MEM_FENCE);
        #pragma unroll UNROLL
        for (uint_t k = 0; k < LSIZE; ++k) {
            jm = _jm[k];
            jrx = _jrx[k];
            jry = _jry[k];
            jrz = _jrz[k];
            je2 = _je2[k];
            jvx = _jvx[k];
            jvy = _jvy[k];
            jvz = _jvz[k];
            nreg_Xkernel_core(
                dt,
                im, irx, iry, irz, ie2, ivx, ivy, ivz,
                jm, jrx, jry, jrz, je2, jvx, jvy, jvz,
                &idrx, &idry, &idrz, &iax, &iay, &iaz, &iu);
        }
    }
    #endif

    for (; j < nj; ++j) {
        real_t jm = __jm[j];
        real_t jrx = __jrx[j];
        real_t jry = __jry[j];
        real_t jrz = __jrz[j];
        real_t je2 = __je2[j];
        real_t jvx = __jvx[j];
        real_t jvy = __jvy[j];
        real_t jvz = __jvz[j];
        nreg_Xkernel_core(
            dt,
            im, irx, iry, irz, ie2, ivx, ivy, ivz,
            jm, jrx, jry, jrz, je2, jvx, jvy, jvz,
            &idrx, &idry, &idrz, &iax, &iay, &iaz, &iu);
    }

    __idrx[gid] = idrx;
    __idry[gid] = idry;
    __idrz[gid] = idrz;
    __iax[gid] = iax;
    __iay[gid] = iay;
    __iaz[gid] = iaz;
    __iu[gid] = im * iu;
}


__attribute__((reqd_work_group_size(LSIZE, 1, 1)))
kernel void
nreg_Vkernel(
    uint_t const ni,
    global real_tn const __im[restrict],
    global real_tn const __ivx[restrict],
    global real_tn const __ivy[restrict],
    global real_tn const __ivz[restrict],
    global real_tn const __iax[restrict],
    global real_tn const __iay[restrict],
    global real_tn const __iaz[restrict],
    uint_t const nj,
    global real_t const __jm[restrict],
    global real_t const __jvx[restrict],
    global real_t const __jvy[restrict],
    global real_t const __jvz[restrict],
    global real_t const __jax[restrict],
    global real_t const __jay[restrict],
    global real_t const __jaz[restrict],
    real_t const dt,
    global real_tn __idvx[restrict],
    global real_tn __idvy[restrict],
    global real_tn __idvz[restrict],
    global real_tn __ik[restrict])
{
    uint_t lid = get_local_id(0);
    uint_t gid = get_global_id(0);
    gid = (gid < ni) ? (gid):(0);

    real_tn im = __im[gid];
    real_tn ivx = __ivx[gid];
    real_tn ivy = __ivy[gid];
    real_tn ivz = __ivz[gid];
    real_tn iax = __iax[gid];
    real_tn iay = __iay[gid];
    real_tn iaz = __iaz[gid];

    real_tn idvx = (real_tn)(0);
    real_tn idvy = (real_tn)(0);
    real_tn idvz = (real_tn)(0);
    real_tn ik = (real_tn)(0);

    uint_t j = 0;

    #ifdef FAST_LOCAL_MEM
    local real_t _jm[LSIZE];
    local real_t _jvx[LSIZE];
    local real_t _jvy[LSIZE];
    local real_t _jvz[LSIZE];
    local real_t _jax[LSIZE];
    local real_t _jay[LSIZE];
    local real_t _jaz[LSIZE];
    for (; (j + LSIZE - 1) < nj; j += LSIZE) {
        real_t jm = __jm[j + lid];
        real_t jvx = __jvx[j + lid];
        real_t jvy = __jvy[j + lid];
        real_t jvz = __jvz[j + lid];
        real_t jax = __jax[j + lid];
        real_t jay = __jay[j + lid];
        real_t jaz = __jaz[j + lid];
        barrier(CLK_LOCAL_MEM_FENCE);
        _jm[lid] = jm;
        _jvx[lid] = jvx;
        _jvy[lid] = jvy;
        _jvz[lid] = jvz;
        _jax[lid] = jax;
        _jay[lid] = jay;
        _jaz[lid] = jaz;
        barrier(CLK_LOCAL_MEM_FENCE);
        #pragma unroll UNROLL
        for (uint_t k = 0; k < LSIZE; ++k) {
            jm = _jm[k];
            jvx = _jvx[k];
            jvy = _jvy[k];
            jvz = _jvz[k];
            jax = _jax[k];
            jay = _jay[k];
            jaz = _jaz[k];
            nreg_Vkernel_core(
                dt,
                im, ivx, ivy, ivz, iax, iay, iaz,
                jm, jvx, jvy, jvz, jax, jay, jaz,
                &idvx, &idvy, &idvz, &ik);
        }
    }
    #endif

    for (; j < nj; ++j) {
        real_t jm = __jm[j];
        real_t jvx = __jvx[j];
        real_t jvy = __jvy[j];
        real_t jvz = __jvz[j];
        real_t jax = __jax[j];
        real_t jay = __jay[j];
        real_t jaz = __jaz[j];
        nreg_Vkernel_core(
            dt,
            im, ivx, ivy, ivz, iax, iay, iaz,
            jm, jvx, jvy, jvz, jax, jay, jaz,
            &idvx, &idvy, &idvz, &ik);
    }

    __idvx[gid] = idvx;
    __idvy[gid] = idvy;
    __idvz[gid] = idvz;
    __ik[gid] = im * ik;
}

