"""
rffi interface to the GNU multiple precision arithmetic library GMP.
"""

from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.lltypesystem import rffi, lltype


info = ExternalCompilationInfo(includes=['gmp.h'], libraries=['gmp'])


## MPZ
MPZ_STRUCT = rffi.COpaque('__mpz_struct', compilation_info=info)
MPZ_PTR = lltype.Ptr(MPZ_STRUCT)

c_mpz_init = rffi.llexternal(
    '__gmpz_init', [MPZ_PTR], lltype.Void, compilation_info=info)
c_mpz_clear = rffi.llexternal(
    '__gmpz_clear', [MPZ_PTR], lltype.Void, compilation_info=info)
c_mpz_set_si = rffi.llexternal(
    '__gmpz_init_set_si', [MPZ_PTR, rffi.LONG], lltype.Void,
    compilation_info=info)
c_mpz_set_ui = rffi.llexternal(
    '__gmpz_set_ui', [MPZ_PTR, rffi.ULONG], lltype.Void, compilation_info=info)
c_mpz_sizeinbase = rffi.llexternal(
    '__gmpz_sizeinbase', [MPZ_PTR, rffi.INT], rffi.SIZE_T,
    compilation_info=info)
c_mpz_get_str = rffi.llexternal(
    '__gmpz_get_str', [rffi.CCHARP, rffi.INT, MPZ_PTR], rffi.CCHARP,
    compilation_info=info)
c_mpz_set_str = rffi.llexternal(
    '__gmpz_set_str', [MPZ_PTR, rffi.CCHARP, rffi.INT], rffi.INT,
    compilation_info=info)
c_mpz_cmp = rffi.llexternal(
    '__gmpz_cmp', [MPZ_PTR, MPZ_PTR], rffi.INT, compilation_info=info)
c_mpz_add = rffi.llexternal(
    '__gmpz_add', [MPZ_PTR, MPZ_PTR, MPZ_PTR], lltype.Void, compilation_info=info)
c_mpz_mul = rffi.llexternal(
    '__gmpz_mul', [MPZ_PTR, MPZ_PTR, MPZ_PTR], lltype.Void, compilation_info=info)
c_mpz_ui_pow_ui = rffi.llexternal(
    '__gmpz_ui_pow_ui', [MPZ_PTR, rffi.ULONG, rffi.ULONG], lltype.Void, compilation_info=info)


## MPQ
MPQ_STRUCT = rffi.COpaque('__mpq_struct', compilation_info=info)
MPQ_PTR = lltype.Ptr(MPQ_STRUCT)

c_mpq_init = rffi.llexternal(
    '__gmpq_init', [MPQ_PTR], lltype.Void, compilation_info=info)
c_mpq_clear = rffi.llexternal(
    '__gmpq_clear', [MPQ_PTR], lltype.Void, compilation_info=info)
c_mpq_canonicalize = rffi.llexternal(
    '__gmpq_canonicalize', [MPQ_PTR], lltype.Void, compilation_info=info)
c_mpq_set_si = rffi.llexternal(
    '__gmpq_set_si', [MPQ_PTR, rffi.LONG, rffi.ULONG], lltype.Void,
    compilation_info=info)
c_mpq_set_ui = rffi.llexternal(
    '__gmpq_set_ui', [MPQ_PTR, rffi.ULONG, rffi.ULONG], lltype.Void,
    compilation_info=info)
c_mpq_set_str = rffi.llexternal(
    '__gmpq_set_str', [MPQ_PTR, rffi.CCHARP, rffi.INT], rffi.INT,
    compilation_info=info)
c_mpq_set_d = rffi.llexternal(
    '__gmpq_set_d', [MPQ_PTR, rffi.DOUBLE], lltype.Void, compilation_info=info)
c_mpq_equal = rffi.llexternal(
    '__gmpq_equal', [MPQ_PTR, MPQ_PTR], rffi.INT, compilation_info=info)
c_mpq_get_num = rffi.llexternal(
    '__gmpq_get_num', [MPZ_PTR, MPQ_PTR], lltype.Void, compilation_info=info)
c_mpq_get_den = rffi.llexternal(
    '__gmpq_get_den', [MPZ_PTR, MPQ_PTR], lltype.Void, compilation_info=info)
c_mpq_set_num = rffi.llexternal(
    '__gmpq_set_num', [MPQ_PTR, MPZ_PTR], rffi.INT, compilation_info=info)
c_mpq_set_den = rffi.llexternal(
    '__gmpq_set_den', [MPQ_PTR, MPZ_PTR], rffi.INT, compilation_info=info)
c_mpq_get_str = rffi.llexternal(
    '__gmpq_get_str', [rffi.CCHARP, rffi.INT, MPQ_PTR], rffi.CCHARP,
    compilation_info=info)
c_mpq_get_d = rffi.llexternal(
    '__gmpq_get_d', [MPQ_PTR], rffi.DOUBLE, compilation_info=info)
c_mpq_set_z = rffi.llexternal(
    '__gmpq_set_z', [MPQ_PTR, MPZ_PTR], lltype.Void, compilation_info=info)
c_mpq_add = rffi.llexternal(
    '__gmpq_add', [MPQ_PTR, MPQ_PTR, MPQ_PTR], lltype.Void, compilation_info=info)


## MPF
MPF_STRUCT = rffi.COpaque('__mpf_struct', compilation_info=info)
MPF_PTR = lltype.Ptr(MPF_STRUCT)
MPF_BITCNT_T = rffi.ULONG
MP_EXP_T = rffi.LONG
MP_EXP_TP = rffi.LONGP

c_mpf_init2 = rffi.llexternal(
    '__gmpf_init2', [MPF_PTR, MPF_BITCNT_T], lltype.Void,
    compilation_info=info)
c_mpf_clear = rffi.llexternal(
    '__gmpf_clear', [MPF_PTR], lltype.Void, compilation_info=info)
c_mpf_set_d = rffi.llexternal(
    '__gmpf_set_d', [MPF_PTR, rffi.DOUBLE], lltype.Void, compilation_info=info)
c_mpf_get_d = rffi.llexternal(
    '__gmpf_get_d', [MPF_PTR], rffi.DOUBLE, compilation_info=info)
c_mpf_set_str = rffi.llexternal(
    '__gmpf_set_str', [MPF_PTR, rffi.CCHARP, rffi.INT], rffi.INT,
    compilation_info=info)
c_mpf_get_str = rffi.llexternal(
    '__gmpf_get_str', [rffi.CCHARP, MP_EXP_TP, rffi.INT, rffi.SIZE_T, MPF_PTR],
    rffi.CCHARP, compilation_info=info)
c_mpf_eq = rffi.llexternal(
    '__gmpf_eq', [MPF_PTR, MPF_PTR, MPF_BITCNT_T], rffi.INT,
    compilation_info=info)
c_mpf_set_z = rffi.llexternal(
    '__gmpf_set_z', [MPF_PTR, MPZ_PTR], lltype.Void, compilation_info=info)
c_mpf_set_q = rffi.llexternal(
    '__gmpf_set_q', [MPF_PTR, MPQ_PTR], lltype.Void, compilation_info=info)
c_mpf_add = rffi.llexternal(
    '__gmpf_add', [MPF_PTR, MPF_PTR, MPF_PTR], lltype.Void, compilation_info=info)
