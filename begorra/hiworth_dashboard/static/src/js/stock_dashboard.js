openerp.stock_dashboard = function(openerp) {
    var _t = openerp.web._t;
    _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;

    openerp.stock_dashboard.StockDashboard = openerp.web.form.FormWidget.extend(openerp.web.form.ReinitializeWidgetMixin, {

        display_name: _lt('Form'),
        view_type: "form",

        init: function() {
            this._super.apply(this, arguments);
           if(this.field_manager.model == "stock.dashboard")
            {
                $(".oe_view_manager_buttons").hide();
                $(".oe_view_manager_header").hide();
            }
            this.set({
                name: false,
                color: false,
            });


        },

        initialize_field: function() {
            openerp.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;

        },

      initialize_content: function() {
           var self = this;
           if (self.setting)
               return;

           if (!this.summary_header || !this.room_summary)
                return;
           // don't render anything until we have summary_header and room_summary

           this.destroy_content();

           if (this.get("summary_header")) {
            this.summary_header = py.eval(this.get("summary_header"));
           }
           if (this.get("room_summary")) {
            this.room_summary = py.eval(this.get("room_summary"));
           }

           this.renderElement();
           this.view_loading();
        },

        view_loading: function(r) {
            return this.load_form(r);
        },



        renderElement: function() {
             this.destroy_content();
             this.$el.html(QWeb.render("summaryDetails", {widget: this}));
        }
    });


    openerp.web.form.custom_widgets.add('Stock_Dashboard', 'openerp.stock_dashboard.StockDashboard');
};
