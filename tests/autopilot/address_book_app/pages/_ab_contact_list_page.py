# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Copyright (C) 2014 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

""" ContactListPage emulator for Addressbook App tests """

import logging
import time

import autopilot.logging
import ubuntuuitoolkit
import address_book_app.address_book as address_book

from autopilot.introspection import dbus
from address_book_app.pages import ABContactViewPage


logger = logging.getLogger(__name__)
log_action_info = autopilot.logging.log_action(logging.info)
log_action_debug = autopilot.logging.log_action(logging.debug)


class ABContactListPage(address_book.PageWithHeader):

    """Autopilot helper for the Contact List page."""

    @log_action_info
    def open_contact(self, index):
        """Open the page with the contact information.

        :param index: The index of the contact to open.
        :return: The page with the contact information.

        """
        contact_delegate = self._get_contact_delegate(index)
        self.pointing_device.click_object(contact_delegate)
        # WORKAROUND: give some time to the view became available
        time.sleep(5.0)
        return self.get_root_instance().select_single(
            ABContactViewPage, objectName='contactViewPage', active=True)

    def _get_contact_delegate(self, index):
        contact_delegates = self._get_sorted_contact_delegates()
        return contact_delegates[index]

    def _get_sorted_contact_delegates(self):
        # FIXME this returns only the contact delegates that are loaded in
        # memory. The list might be big, so not all delegates might be in
        # memory at the same time.
        contact_delegates = self.select_many('ContactDelegate', visible=True)
        return sorted(
            contact_delegates, key=lambda delegate: delegate.globalRect.y)

    @log_action_info
    def select_contacts(self, indices):
        """ Select contacts corresponding to the list of index in indices

        :param indices: List of integers

        """
        self._deselect_all()
        if len(indices) > 0:
            view = self._get_list_view()
            if not view.isInSelectionMode:
                self._start_selection(indices[0])
                indices = indices[1:]

            for index in indices:
                contact = self._get_contact_delegate(index)
                self.pointing_device.click_object(contact)

    @log_action_debug
    def _deselect_all(self):
        """Deselect all contacts."""
        view = self._get_list_view()
        if view.isInSelectionMode:
            contacts = self.select_many('ContactDelegate', visible=True)
            for contact in contacts:
                if contact.selected:
                    logger.info('Deselect {}.'.format(contact.objectName))
                    self.pointing_device.click_object(contact)
        else:
            logger.debug('The page is not in selection mode.')

    def _start_selection(self, index):
        # TODO change this for click_object once the press duration
        # parameter is added. See http://pad.lv/1268782
        contact = self._get_contact_delegate(index)
        self.pointing_device.move_to_object(contact)
        self.pointing_device.press()
        time.sleep(2.0)
        self.pointing_device.release()
        view = self._get_list_view()
        view.isInSelectionMode.wait_for(True)

    def _get_list_view(self):
        return self.wait_select_single(
            'ContactListView', objectName='contactListView')

    @log_action_info
    def delete_selected_contacts(self, main_window):
        main_window.delete()
        main_window.wait_bottom_edge(False)
        dialog = self.get_root_instance().wait_select_single(
            address_book.RemoveContactsDialog, objectName='removeContactsDialog')
        dialog.confirm_removal()

    def get_contacts(self):
        """Return a list with the names of the contacts."""
        contact_delegates = self._get_sorted_contact_delegates()
        name_labels = [
            delegate.select_single('UCLabel', objectName='nameLabel') for
            delegate in contact_delegates
        ]
        return [label.text for label in name_labels]

    def get_button(self, buttonName):
        try:
            return self.get_header()._get_action_button(buttonName)
        except ubuntuuitoolkit.ToolkitException:
            return None

    def is_import_from_sim_button_visible(self):
        import_from_sim_button = self.select_single(
            'ContactListButtonDelegate',
            objectName='contactListView.importFromSimCardButton')
        return import_from_sim_button.visible
