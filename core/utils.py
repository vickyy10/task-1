from django.contrib.auth.decorators import login_required, user_passes_test


def is_superadmin(user):
    return user.is_authenticated and user.is_superadmin

def is_admin(user):
    return user.is_authenticated and (user.is_admin or user.is_superadmin)

def is_superadmin_or_admin(user):
    return user.is_authenticated and (user.is_admin or user.is_superadmin)

# SuperAdmin required decorator
def superadmin_required(view_func):
    decorated_view_func = login_required(user_passes_test(
        is_superadmin, 
        login_url='login',
        redirect_field_name=None
    )(view_func))
    return decorated_view_func

# Admin required decorator
def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(
        is_admin, 
        login_url='login',
        redirect_field_name=None
    )(view_func))
    return decorated_view_func

# SuperAdmin or Admin required decorator
def superadmin_or_admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(
        is_superadmin_or_admin, 
        login_url='login',
        redirect_field_name=None
    )(view_func))
    return decorated_view_func