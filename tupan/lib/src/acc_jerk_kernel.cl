#include "acc_jerk_kernel_common.h"

inline void acc_jerk_kernel_main_loop(
    const REAL im,
    const REAL irx,
    const REAL iry,
    const REAL irz,
    const REAL ie2,
    const REAL ivx,
    const REAL ivy,
    const REAL ivz,
    const uint nj,
    __global const REAL *_jm,
    __global const REAL *_jrx,
    __global const REAL *_jry,
    __global const REAL *_jrz,
    __global const REAL *_je2,
    __global const REAL *_jvx,
    __global const REAL *_jvy,
    __global const REAL *_jvz,
    __local REAL *__jm,
    __local REAL *__jrx,
    __local REAL *__jry,
    __local REAL *__jrz,
    __local REAL *__je2,
    __local REAL *__jvx,
    __local REAL *__jvy,
    __local REAL *__jvz,
    REAL *iax,
    REAL *iay,
    REAL *iaz,
    REAL *ijx,
    REAL *ijy,
    REAL *ijz)
{
    uint lsize = get_local_size(0);
    uint ntiles = (nj - 1)/lsize + 1;

    for (uint tile = 0; tile < ntiles; ++tile) {
        uint nb = min(lsize, (nj - (tile * lsize)));

        event_t e[8];
        e[0] = async_work_group_copy(__jm,  _jm  + tile * lsize, nb, 0);
        e[1] = async_work_group_copy(__jrx, _jrx + tile * lsize, nb, 0);
        e[2] = async_work_group_copy(__jry, _jry + tile * lsize, nb, 0);
        e[3] = async_work_group_copy(__jrz, _jrz + tile * lsize, nb, 0);
        e[4] = async_work_group_copy(__je2, _je2 + tile * lsize, nb, 0);
        e[5] = async_work_group_copy(__jvx, _jvx + tile * lsize, nb, 0);
        e[6] = async_work_group_copy(__jvy, _jvy + tile * lsize, nb, 0);
        e[7] = async_work_group_copy(__jvz, _jvz + tile * lsize, nb, 0);
        wait_group_events(8, e);

        for (uint j = 0; j < nb; ++j) {
            REAL jm = __jm[j];
            REAL jrx = __jrx[j];
            REAL jry = __jry[j];
            REAL jrz = __jrz[j];
            REAL je2 = __je2[j];
            REAL jvx = __jvx[j];
            REAL jvy = __jvy[j];
            REAL jvz = __jvz[j];
            acc_jerk_kernel_core(im, irx, iry, irz, ie2, ivx, ivy, ivz,
                                 jm, jrx, jry, jrz, je2, jvx, jvy, jvz,
                                 &(*iax), &(*iay), &(*iaz),
                                 &(*ijx), &(*ijy), &(*ijz));
        }

        barrier(CLK_LOCAL_MEM_FENCE);
    }
}


__kernel void acc_jerk_kernel(
    const uint ni,
    __global const REAL *_im,
    __global const REAL *_irx,
    __global const REAL *_iry,
    __global const REAL *_irz,
    __global const REAL *_ie2,
    __global const REAL *_ivx,
    __global const REAL *_ivy,
    __global const REAL *_ivz,
    const uint nj,
    __global const REAL *_jm,
    __global const REAL *_jrx,
    __global const REAL *_jry,
    __global const REAL *_jrz,
    __global const REAL *_je2,
    __global const REAL *_jvx,
    __global const REAL *_jvy,
    __global const REAL *_jvz,
    __global REAL *_iax,
    __global REAL *_iay,
    __global REAL *_iaz,
    __global REAL *_ijx,
    __global REAL *_ijy,
    __global REAL *_ijz,
    __local REAL *__jm,
    __local REAL *__jrx,
    __local REAL *__jry,
    __local REAL *__jrz,
    __local REAL *__je2,
    __local REAL *__jvx,
    __local REAL *__jvy,
    __local REAL *__jvz)
{
    uint gid = get_global_id(0);
    uint i = min(gid, ni-1);

    REAL im = _im[i];
    REAL irx = _irx[i];
    REAL iry = _iry[i];
    REAL irz = _irz[i];
    REAL ie2 = _ie2[i];
    REAL ivx = _ivx[i];
    REAL ivy = _ivy[i];
    REAL ivz = _ivz[i];

    REAL iax = 0;
    REAL iay = 0;
    REAL iaz = 0;
    REAL ijx = 0;
    REAL ijy = 0;
    REAL ijz = 0;

    acc_jerk_kernel_main_loop(
        im, irx, iry, irz, ie2, ivx, ivy, ivz,
        nj,
        _jm, _jrx, _jry, _jrz, _je2, _jvx, _jvy, _jvz,
        __jm, __jrx, __jry, __jrz, __je2, __jvx, __jvy, __jvz,
        &iax, &iay, &iaz,
        &ijx, &ijy, &ijz);

    _iax[i] = iax;
    _iay[i] = iay;
    _iaz[i] = iaz;
    _ijx[i] = ijx;
    _ijy[i] = ijy;
    _ijz[i] = ijz;
}

