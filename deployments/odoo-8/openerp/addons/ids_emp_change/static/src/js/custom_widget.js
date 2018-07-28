openerp.ids_emp_change = function (instance) {
    instance.web.form.widgets.add('change_color', 'instance.ids_emp_change.change_color');
    instance.ids_emp_change.change_color = instance.web.form.FieldChar.extend({
        _format: function (row_data, options) {
            res = this._super.apply(this, arguments);
            var amount = parseFloat(res);
            if (amount < 0){
                return "<font color='#ff0000'>"+(-amount)+"</font>";
            }
            return res;
        }
    });
    //
    //here you can add more widgets if you need, as above...
    //
};

