"""Small cross-platform runtime helpers."""
import sys


def peak_rss_mib():
    """Return OS-reported peak RSS where supported, otherwise explicit missing."""
    try:
        import resource
    except ImportError:
        return None
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(value/(1024*1024 if sys.platform=='darwin' else 1024),2)
