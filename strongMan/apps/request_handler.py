from collections import OrderedDict

from django.contrib import messages
from django.shortcuts import render

from strongMan.apps.vici.wrapper.exception import ViciSocketException, ViciLoadException
from strongMan.apps.vici.wrapper.wrapper import ViciWrapper
from .forms import PasswordChangeForm


class AboutHandler:
    def __init__(self, request):
        self.request = request

    def _render_page(self, form=PasswordChangeForm()):
        context = OrderedDict()

        try:
            vici_wrapper = ViciWrapper()
            context = vici_wrapper.get_version()
            context['plugins'] = vici_wrapper.get_plugins()
        except ViciLoadException as e:
            messages.warning(self.request, str(e))
        except ViciSocketException as e:
            pass
        context["pw_form"] = form
        return render(self.request, 'about.html', context)

    def handle(self):
        if self.request.method == "GET":
            return self._render_page()
        if self.request.method == "POST":
            form = PasswordChangeForm(self.request.POST)
            if not form.is_valid():
                for msg in form.error_msg:
                    messages.warning(self.request, msg)
                return self._render_page()
            try:
                self._change_password(form)
                messages.info(self.request, "Password changed successfully!")
            except AboutException as e:
                messages.error(self.request, str(e))
            return self._render_page()

    def _change_password(self, form):
        user = self.request.user
        if not user.check_password(form.old_pw):
            raise AboutException("Current password is wrong!")
        if not form.pw1 == form.pw2:
            raise AboutException("New passwords are not equal!")
        if not self._is_password_hard(form.pw1):
            raise AboutException("Your new password isn't hard enough! Follow the password rules below.")

        user.set_password(form.pw1)
        user.save()

    def _is_password_hard(self, password):
        '''
        Checks if the password has a certain quality.
        Length > 7
        password needs a non alphabetic sign
        password has a lower and a upper case sign at least
        :param password: password to check
        :return: Boolean
        '''
        if len(password) < 8:
            return False

        if password.isalpha():
            return False

        if not self._has_upper(password):
            return False

        if not self._has_lower(password):
            return False

        if not self._has_digit(password):
            return False

        return True

    def _has_upper(self, password):
        for letter in password:
            if letter.isupper():
                return True
        return False

    def _has_lower(self, password):
        for letter in password:
            if letter.islower():
                return True
        return False

    def _has_digit(self, password):
        for letter in password:
            if letter.isdigit():
                return True
        return False


class AboutException(Exception):
    pass
