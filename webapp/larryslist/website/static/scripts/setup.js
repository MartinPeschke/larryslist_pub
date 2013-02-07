(function (root, root_options) {
    var
        gF = $("#global-frame"), bW = parseInt(gF.css("border-width").replace(/[a-z]/g,''), 10)
        , resizeFrame = function(e){
            var wH = $(window).height();
            if(gF.height() < wH){gF.css({height:(wH-2*bW)+"px"})}
        };
        $(window).on({resize: resizeFrame});
        resizeFrame();

    var login = $("#login-pull-down-form")
    if(login.length){
        require(["tools/ajax"], function(ajax){
            ajax.ifyForm({root:login});
        });
    }
    require(["site"]);
})(hnc, window.__options__);