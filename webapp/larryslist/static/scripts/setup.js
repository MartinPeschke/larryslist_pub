(function(root){
    _.templateSettings = {
        interpolate : /\{\{ (.+?) \}\}/g
        , evaluate: /\{% (.+?) %\}/g
    };
    // IE<9
    if(typeof String.prototype.trim !== 'function') {
        String.prototype.trim = function() {
            return this.replace(/^\s+|\s+$/g, '');
        }
    }
    var _isTouch = !!('ontouchstart' in window && '__proto__' in {})
        , HNC = function(options){
            this.options = options;
            this.initialize.apply(this, arguments);
            var ctor = function(){}
                , inherits = function(parent, protoProps, staticProps) {
                    var child;
                    if (protoProps && protoProps.hasOwnProperty('constructor')) {
                        child = protoProps.constructor;
                    } else {
                        child = function(){ parent.apply(this, arguments); };
                    }
                    ctor.prototype = parent.prototype;
                    child.prototype = new ctor();
                    if (protoProps) _.extend(child.prototype, protoProps);
                    if (staticProps) _.extend(child, staticProps);
                    child.prototype.constructor = child;
                    child.__super__ = parent.prototype;
                    return child;
                };
            this.extend = function (protoProps, classProps) {
                var child = inherits(this, protoProps, classProps);
                child.extend = this.extend;
                return child;
            };
        };

        _.extend(HNC.prototype, Backbone.Events, {
            initialize: function(options){}
            , rld: function(){
                window.location.href = "//" + window.location.host + window.location.pathname + '?' + window.location.search;
            }
            , getRecursive: function(obj, key, defaults){
                var tmp = obj, keys = key.split("."), i= 0, len = keys.length;
                for (;i<len;i++) {
                    if(tmp.hasOwnProperty(keys[i])){
                        tmp = tmp[keys[i]];
                    } else {
                        return defaults;
                    }
                }
                return tmp;
            }
            , apiUrl: function (path){
                return '/api/'+this.api_version+path;
            }
            , resUrl: function(path){
                return '//'+this.options.resourceHost +'/'+ path;
            }
            , isPicturePath: function(path){
                return /(jpg|png|gif|bmp|tiff|tga)$/.test(path.toLowerCase())
            }
            , validate : function(params){
                var form = params.root.is("form.form-validated") ? params.root : params.root.find("form.form-validated")
                var opts = _.extend({
                        errorClass: "help-inline"
                        , errorElement: "span"
                        , validClass:"valid"
                        , onkeyup: false
                        , highlight: function (element, errorClass, validClass) {
                            $(element).closest(".control-group").addClass("error").removeClass(validClass).removeClass(validClass);
                        }
                        , unhighlight: function (element, errorClass, validClass) {
                            var name = $(element).attr("name");
                            if(name && $(element).closest(".controls").find('[for='+name.replace(/\./g,"\\.")+']').filter("[generated]").remove().length)
                                $(element).closest(".control-group").removeClass("error").addClass(validClass);
                        }
                    }, params)
                    , validator = $(form).validate(opts)
                    , view = this;

                $(form).find("input[type=reset], button[type=reset]").click(function(e) {
                    view.resetForm(form);
                });

                $(form).find("[data-validation-url]").each(function(idx, elem){
                    var $elem = $(elem);
                    $elem.rules("add", {remote: $elem.data("validationUrl")});
                });

                if(params.focus){
                    form.find("input,select,textarea").filter(":visible").first().focus();
                }
                return validator;
            }
            , resetForm: function(form){
                var $f = $(form)
                $f.validate().resetForm();
                $f.find(".error").removeClass("error");
                $f.find("[generated]").remove();
            }
            , zeroFill: function( number, width ) {
                width -= number.toString().length;
                if ( width > 0 )
                {
                    return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
                }
                return number + ""; // always return a string
            }
            , support : {
                clickEvent : _isTouch?"touchstart":"click"
                , touchStartEvent: _isTouch?"touchstart":"mousedown"
            }
            , translate: function(s){return s;}
            // LOCALE AWARE
            , parseDate: function(input, format) {
                format = format || 'yyyy-mm-ddTHH:MM:SS'; // default format
                var parts = input.match(/(\d+)/g),
                    i = 0, fmt = {};
                // extract date-part indexes from the format
                format.replace(/(yyyy|dd|mm|HH|MM|SS)/g, function(part) { fmt[part] = i++; });
                return new Date(parts[fmt.yyyy], parts[fmt.mm]-1, parts[fmt.dd], parts[fmt.HH]||0, parts[fmt.MM]||0, parts[fmt.SS]||0);
            }
            , formatCurrency: function(num, currency){
                if(LOCALE=='de'){
                    return hnc.formatNumber(num)+" "+CURRENCY[currency];
                } else {
                    return CURRENCY[currency]+" "+hnc.formatNumber(num);
                }
            }
            , formatNumber: function(num, dec){
                var val = num.toFixed(dec||2);
                if(LOCALE=='de')
                    return val.replace(/\./g, DECSEP);
                else
                    return val;
            }

        });

        // Bootstrap Touch Devices DropDown Fix START
        $('body')
        .on('touchstart.dropdown', '.dropdown-menu', function (e) { e.stopPropagation(); })
        .on('touchstart.dropdown', '.dropdown-submenu', function (e) { e.preventDefault(); })
        // Bootstrap Form inside dropdown prevent close
        .on("click", '.dropdown input, .dropdown label', function(e){e.stopPropagation();});
        // Bootstrap Touch Devices DropDown Fix END

        // TOGGLEABLE FLY OUTS
        $(document).on({click: function(e){
            var $t = $(e.currentTarget), data = $t.data(), target = data.toggleTarget, toggle = data.toggleClass
                , on = (target?$t.closest(target):$t).toggleClass(toggle).hasClass(toggle);
            if(data.toggleText){
                if(on){
                    $t.data("backupText", $t.html());
                    $t.html(data.toggleText);
                } else {
                    $t.html(data.backupText);
                }
            }
        }}, "[data-toggle-class]");
        // hiding server generated messages
        var mCont = $("#message-container");
        if(mCont.length){
            mCont.on({click: function(e){
                var $t = $(this).closest(".alert");
                if(!$t.siblings(".alert").length)
                    mCont.hide();
                $t.remove();
            }}, '[data-dismiss="alert"]');
            $(document).on({scroll: function(e){
                    var messageTop = mCont.position().top;
                    mCont[$(window).scrollTop()>messageTop?"addClass":"removeClass"]("fixed")
            }});
        }
        // IE placeholder plugin
        var NATIVE_PLACEHOLDER = !!("placeholder" in document.createElement( "input" ));
        if(!NATIVE_PLACEHOLDER){
            $('input[placeholder], textarea[placeholder]').placeholder();
        }
        _.extend(HNC, Backbone.Events);
        root.hnc = new HNC(window.__options__);

        jQuery.validator.addMethod("tagsearch-required", function (value, element) {
            return $(element).closest(".tagsearch-container").find(".tag").length > 0;
        }, hnc.translate("Please add at least one tag."));
    })(window);