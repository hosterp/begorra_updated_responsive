openerp.hamburger_menu = function(instance) {
    "use strict";

    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var utils = instance.web.utils;

    $(document).ready(function() {
        // Get the menu item element
        var menuItem = document.getElementById('base.menu_purchase_root');

        // Add a hamburger menu icon before the submenu
        var hamburgerIcon = document.createElement('span');
        hamburgerIcon.className = 'hamburger-menu-icon';
        hamburgerIcon.innerHTML = '<i class="fa fa-bars"></i>';
        menuItem.insertBefore(hamburgerIcon, menuItem.firstElementChild);

        // Add an event listener to the hamburger menu icon
        hamburgerIcon.addEventListener('click', function() {
            // Toggle the submenu visibility
            menuItem.classList.toggle('show');
        });
    });
};