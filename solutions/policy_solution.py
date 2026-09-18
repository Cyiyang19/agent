def choose_next(status):
    return 'search' if status == 'retry' else 'end'
