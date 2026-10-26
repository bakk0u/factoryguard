"""Small cross-platform runtime helpers."""
import sys
import os
from pathlib import Path


def raw_storage_root():
    """Dataset parent containing archives and raw/, resolved on the current OS."""
    return Path(os.environ.get('FACTORYGUARD_RAW_ROOT',
                              '/workspace/datasets/paderborn-10868257')).expanduser().resolve()


def protect_output(path, *additional_roots):
    """Resolve both sides and reject source writes before any directory creation."""
    output = Path(path).expanduser().resolve()
    roots = [raw_storage_root(), *(Path(p).expanduser().resolve() for p in additional_roots)]
    if any(output == root or root in output.parents for root in roots):
        raise ValueError('Outputs must be separate from immutable source storage')
    return output


def peak_rss_mib():
    """Return OS-reported peak RSS where supported, otherwise explicit missing."""
    try:
        import resource
    except ImportError:
        return None
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(value/(1024*1024 if sys.platform=='darwin' else 1024),2)
