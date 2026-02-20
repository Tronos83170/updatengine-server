###############################################################################
# UpdatEngine - Software Packages Deployment and Administration tool         #
#                                                                             #
# Copyright (C) Yves Guimard - yves.guimard@gmail.com                        #
# Copyright (C) Noel Martinon - noel.martinon@gmail.com                      #
#                                                                             #
# This program is free software; you can redistribute it and/or              #
# modify it under the terms of the GNU General Public License                #
# as published by the Free Software Foundation; either version 2             #
# of the License, or (at your option) any later version.                     #
#                                                                             #
# This program is distributed in the hope that it will be useful,            #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the               #
# GNU General Public License for more details.                               #
#                                                                             #
# You should have received a copy of the GNU General Public License          #
# along with this program; if not, write to the Free Software Foundation,    #
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.         #
###############################################################################
from django.urls import include, path, re_path, reverse_lazy
from django.contrib import admin
from inventory.views import post
from django.contrib.admin import site
import adminactions.actions as actions
from .views import check_version, ChangePasswordView, ChangePasswordDoneView

# Import admin module in each installed application
admin.autodiscover()

# Register all adminactions
site.add_action(actions.mass_update)
site.add_action(actions.export_as_csv)

urlpatterns = [
    # Modern UI (namespaced: 'modern')
    path('modern/', include('updatengine.urls_modern', namespace='modern')),

    # Legacy & API
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^inventory/', include('inventory.urls')),
    re_path(r'^repository/', include('repository.urls')),
    re_path(r'^deployment/', include('deployment.urls')),
    re_path(r'^check_version/', check_version),
    re_path(r'^post/', post),

    # Auth
    re_path(r'^password_change/$', ChangePasswordView.as_view(), name='password_change'),
    re_path(r'^password_change/done/$', ChangePasswordDoneView.as_view(), name='password_change_done'),
    re_path(r'^', include('django.contrib.auth.urls')),
]
