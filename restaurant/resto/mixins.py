# restaurant/mixins.py

from django.contrib.auth.mixins import UserPassesTestMixin

class GroupRequiredMixin(UserPassesTestMixin):
    group_name = None

    def test_func(self):
        return self.request.user.groups.filter(name=self.group_name).exists() or self.request.user.is_superuser
