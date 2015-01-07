from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.lltypesystem import rffi, lltype
from rpython.rlib.rarithmetic import r_uint

info = ExternalCompilationInfo(
    includes=['gmp.h'],
    libraries=['gmp']
)

MPZ_STRUCT = rffi.COpaque('__mpz_struct', compilation_info=info)
MPZ_PTR = lltype.Ptr(MPZ_STRUCT)

c_mpz_init = rffi.llexternal(
    '__gmpz_init', [MPZ_PTR], lltype.Void, compilation_info=info)
c_mpz_clear = rffi.llexternal(
    '__gmpz_clear', [MPZ_PTR], lltype.Void, compilation_info=info)

c_mpz_set_si = rffi.llexternal(
    '__gmpz_init_set_si', [MPZ_PTR, rffi.LONG], lltype.Void, compilation_info=info)
# c_mpz_set_ui = rffi.llexternal(
#     '__gmpz_set_ui', [MPZ_PTR, lltype.Unsigned], lltype.Void, compilation_info=info)

c_mpz_sizeinbase = rffi.llexternal(
    '__gmpz_sizeinbase', [MPZ_PTR, rffi.INT], rffi.SIZE_T, compilation_info=info)
c_mpz_get_str = rffi.llexternal(
    '__gmpz_get_str', [rffi.CCHARP, rffi.INT, MPZ_PTR], rffi.CCHARP, compilation_info=info)
c_mpz_set_str = rffi.llexternal(
    '__gmpz_set_str', [MPZ_PTR, rffi.CCHARP, rffi.INT], rffi.INT, compilation_info=info)

c_mpz_cmp = rffi.llexternal(
    '__gmpz_cmp', [MPZ_PTR, MPZ_PTR], rffi.INT, compilation_info=info)
