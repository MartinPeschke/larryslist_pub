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


    var LOCALE = $('html').attr('lang'), THOUSEP = LOCALE=='de'?".":",", DECSEP = LOCALE=='de'?",":"."
        , CURRENCY = {EUR:'&euro;'}
        , _isTouch = !!('ontouchstart' in window && '__proto__' in {})
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
                        if(typeof tmp === 'undefined'){
                            return defaults;
                        }
                    }
                }
                return tmp;
            }
            , apiUrl: function (path){
                return '/api/'+this.api_version+path;
            }
            , send: function (options) {
                var params = _.extend({
                    type: "POST"
                    , dataType: "json"
                    , headers: {'Client-Token': this.options.clientToken}
                    , contentType: "application/json; charset=utf-8"
                }, options || {});
                params.success = function (resp, status, xhr) {
                    if (resp.redirect) {
                        window.location.href = resp.redirect;
                    } else if (options.success) options.success.apply(this, arguments);
                };
                if (typeof params.data != 'string') { params.data = JSON.stringify(params.data) }
                $.ajax(params);
            }
            , sendAuthed : function(options){
                options.headers = {'Client-Token': this.options.clientToken};
                this.send(options);
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
                            if($(element).closest(".controls").find('[for='+$(element).attr("name").replace(/\./g,"\\.")+']').filter("[generated]").remove().length)
                                $(element).closest(".control-group").removeClass("error").addClass(validClass);
                        }
                        , success: function(label, element){
                            $(element).closest(".control-group").removeClass("error").addClass(this.validClass);
                        }
                        , errorPlacement: function(error, element) {
                            if(element.parent().find("."+this.errorClass+"[generated=true]").length)return;
                            if (element.parent().is(".input-append"))
                                error.insertAfter(element.parent());
                            else
                                error.appendTo(element.closest(".controls"));
                        }
                    }, params)
                    , validator = $(form).validate(opts)
                    , view = this;

                $(form).find("input[type=reset], button[type=reset]").click(function(e) {
                    view.resetForm(form);
                });
                var add = $(form).find(".timeShort");
                if(add.length)add.rules("add", {timeShort:true});
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
            , resolve_resource : function (path) {
                if(!path||path.slice(0,4) == 'http')return path;
                if(path[0] == '/') path = path.substr(1);
                return window.location.protocol + '//' + this.reshost + path;
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
            var $t = $(e.currentTarget), target = $t.attr("data-toggle-target"), toggle = $t.attr("data-toggle-class")
                , on = (target?$t.closest(target):$t).toggleClass(toggle).hasClass(toggle);
            if($t.attr("data-toggle-text")){
                if(on){
                    $t.attr("data-backup-text", $t.html());
                    $t.html($t.attr("data-toggle-text"));
                } else {
                    $t.html($t.attr("data-backup-text"));
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

        hnc.on("i18n:available", function(){
            jQuery.validator.addMethod("phone-number", function (value, element) {
                return this.optional(element) || /^[+]?([0-9]+[()/-]?)+$/gi.test(value.replace(/ /g, ""));
            }, hnc.translate("Please enter a phone number."));
            jQuery.validator.addMethod("timeShort", function (value, element) {
                return this.optional(element) ||/^([0-1][0-9]+|2[0-3])(:[0-5][0-9]){1,2}$/gi.test(value.replace(/ /g, ""));
            }, hnc.translate("Please enter a valid time, like HH:MM."));
            jQuery.validator.addMethod("date-field", function (value, element) {
                return this.optional(element) ||/^(19[0-9]{2}|20[0-9]{2}-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01]))$/gi.test(value.replace(/ /g, ""));
            }, hnc.translate("Please enter a valid date, like yyyy-mm-dd"));
            jQuery.validator.methods.number = function (value, element) {
                return this.optional(element) || /^-?(?:\d+|\d{1,3}(?:[\s\.]\d{3})+)(?:[,]\d+)?$/.test(value);
            };
            jQuery.validator.methods.range = function (value, element, param) {
                var globalizedValue = parseFloat(value.replace(/\./g, "").replace(/\,/g, "."));
                return this.optional(element) || (globalizedValue >= param[0] && globalizedValue <= param[1]);
            };
            $.validator.autoCreateRanges = true;
        });
        $(".goal-progress-bar").find(".progress-marker-pin").one({
            mouseenter: function(e){
                var data = $(e.target).data();
                if(!data.workoutId)return;
                require(['/ajax/callback/workout/'+data.workoutId], function(card){
                    if(card.html){
                        $(e.target).append(card.html);
                    } else if(card.redirect){
                        window.location.href = card.redirect;
                    }
                });
            }
        });
    })(window);