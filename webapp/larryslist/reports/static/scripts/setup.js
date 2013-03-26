(function(root){
    _.templateSettings = {
        interpolate : /\{\{ (.+?) \}\}/g
        , evaluate: /\{% (.+?) %\}/g
    };

    var
        mod = 'modernizr', modElem = document.createElement(mod)
        , mStyle = modElem.style
        , domPrefixes = 'Webkit Moz O ms Khtml'.split(' ')
        , testProps = function (props, prefixed) {
            for (var i in props)
                if (mStyle[props[i]] !== undefined)
                    return prefixed == 'pfx' ? props[i] : true;
            return false;
        }
            , testPropsAll = function (prop, prefixed) {
            var ucProp = prop.charAt(0).toUpperCase() + prop.substr(1),
                props = (prop + ' ' + domPrefixes.join(ucProp + ' ') + ucProp).split(' ');
            return testProps(props, prefixed);
        }
        , slice = Array.prototype.slice
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
            if(_.isEmpty(tmp))return defaults;
            for (;i<len;i++) {
                if(tmp.hasOwnProperty(keys[i])){
                    tmp = tmp[keys[i]];
                } else {
                    return defaults;
                }
            }
            return tmp;
        }
        , validate : function(params){
            var form = params.root.is("form.form-validated") ? params.root : params.root.find("form.form-validated")
            var opts = _.extend({
                    errorClass: "help-inline"
                    ,errorElement: "span"
                    ,onkeyup: false
                    , highlight: function (element, errorClass, validClass) {
                        $(element).closest(".control-group").addClass("error").removeClass(validClass);
                    }
                    , unhighlight: function (element, errorClass, validClass) {
                        if($(element).closest(".controls").find('[for='+$(element).attr("name").replace(/\./g,"\\.")+']').filter("[generated]").remove().length)
                            $(element).closest(".control-group").removeClass("error").addClass(validClass);
                    }
                    , errorPlacement: function(error, element) {
                        if(element.parent().find("."+this.errorClass+"[generated=true]").length)return;
                        if (element.parent().is(".input-append"))
                            error.insertAfter(element.parent());
                        else
                            error.appendTo(element.closest(".controls"));
                    }
                }, params)
                , validator = $(form).validate(opts);
            $(form).find("input[type=reset], button[type=reset]").click(function(e) {
                validator.resetForm();
                $(form).find(".error").removeClass("error");
                $(form).find("[generated]").remove();
            });
            var add = $(form).find(".timeShort");
            if(add.length)add.rules("add", {timeShort:true});
            if(params.focus){
                form.find("input,select,textarea").filter(":visible").first().focus();
            }
            return validator;
        }
        , resolve_resource : function (path) {
            if(!path||path.slice(0,4) == 'http')return path;
            if(path[0] == '/') path = path.substr(1);
            return window.location.protocol + '//' + this.reshost + path;
        }
        , gotoUrl: function (url) {
            return function () { window.location.href = url; }
        }
        , parseDate: function(input, format) {
            format = format || 'yyyy-mm-ddTHH:MM:SS'; // default format
            var parts = input.match(/(\d+)/g),
                i = 0, fmt = {};
            // extract date-part indexes from the format
            format.replace(/(yyyy|dd|mm|HH|MM|SS)/g, function(part) { fmt[part] = i++; });
            return new Date(parts[fmt.yyyy], parts[fmt.mm]-1, parts[fmt.dd], parts[fmt.HH]||0, parts[fmt.MM]||0, parts[fmt.SS]||0);
        }
        , getUserPicture: function(user){
            if(user.picture)return user.picture
            else {
                var email = user.email;
                if(!email){
                    return "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm";
                } else {
                    return "//www.gravatar.com/avatar/"+this.hashlib.md5(email)+"?d=mm";
                }
            }
        }
        , apiUrl: function (path){
            return '/api/'+this.api_version+path;
        }
        , send: function (options) {
            var params = _.extend({
                type: "POST"
                , dataType: "json"
                , headers: {'Client-Token': this.options.client.token}
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
        , sendAuthed: function(options){
            options.headers = {'Authorisation-Token': this.options.user.token};
            this.send(options);
        }
        , deferreds: function (doneFunc, context) {
            var deferreds = [], _t = this;
            this.doneFunc = doneFunc;
            this.add = function (f) {
                deferreds.push(f);
                _t.run(arguments);
            };
            this.run = function () {
                if (_t.doneFunc.apply(context)) {
                    var i = 0; len = deferreds.length;
                    for (; i < len; i++) {
                        var f = deferreds.pop();
                        f.apply(_t, arguments);
                    }
                }
            };
        }
        , support : {
            cssTransitions : testPropsAll('transitionProperty')
            , clickEvent : !!('ontouchstart' in window && '__proto__' in {})?"touchstart":"click"
            , touchStartEvent: !!('ontouchstart' in window && '__proto__' in {})?"touchstart":"mousedown"
        }
    });
    root.hnc = new HNC(window.__options__);
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
    hnc.translate = function(s){
        return s==null ? s : s.split("_").join(" ");
    };
    hnc.title = function(s){return s.split("_").join(" ");};
})(window);