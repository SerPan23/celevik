from django.contrib.auth.decorators import user_passes_test, login_required


def is_Company(self):
    if str(self.user_info.role) == 'Company':
        return True
    return False


def is_Admin(self):
    if str(self.user_info.role) == 'Admin':
        return True
    return False


comp_login_required = user_passes_test(lambda u: True if is_Company(u) else False, login_url='/?is_not_comp=True')
adm_login_required = user_passes_test(lambda u: True if is_Admin(u) else False, login_url='/?is_not_adm=True')


def company_login_required(view_func):
    decorated_view_func = login_required(comp_login_required(view_func))
    return decorated_view_func


def admin_login_required(view_func):
    decorated_view_func = login_required(adm_login_required(view_func))
    return decorated_view_func


def is_intersection_list(list1, list2):
    res = set(list1).intersection(list2)
    if len(res) > 0:
        return True
    return False
