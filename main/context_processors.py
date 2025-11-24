
def total_data(request):
    if request.user.is_authenticated:
        branch = request.user.branch
        user = request.user
    else:
        branch=None
        user=None
    context = {
        'branch': branch,
        'user': user,
    }
    return context