define(["tools/ajax", "tools/config", "text!templates/address.html"], function(ajax, config, tmpl){
    var

        template = _.template(tmpl)

        , hide = function(root) {
            root.find('input[name$="Country.name"]').closest(".control-group").nextAll().andSelf().hide().find("input").each(function(idx, elem){
                elem.value = '';
            });
            root.find('input[name$="other_name"]').val("");
        }
        , onChange = function(root, $el, config){
            var museum = config.getMuseum($el.val());
            root.find('.dynamic-address-fields').remove();
            if(museum){
                hide(root);

                root.append(template({
                    model: museum
                }));
            } else {
                root.find('input[name$="Country.name"]').closest(".control-group").nextAll().andSelf().show();
            }
        }
        , init = function(opts){
            var el = $(opts.el), root = el.closest("[data-sequence], .form-validated")
                , preselected = el.find("option").filter(":selected");

            config.fetch(function(cfg){
                el.on({change: function(e){
                    onChange(root, $(e.target), cfg);
                }});
                onChange(root, preselected, cfg);
            }, this);


        };
    return {init:init};
});