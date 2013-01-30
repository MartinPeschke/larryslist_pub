define(["tools/hash", "plupload"], function (hashlib) {

var M = Math, P = M.pow(10,12)
        FileUploadView = Backbone.View.extend({
        uploading_template:
                    _.template('<div id="{{ id }}" class="upload-progress"><b>0%</b> {{ name }} ({{ (size/1024).toFixed(0) }}K)<div class="progress"><div class="bar"></div></div></div>')
        , error_template: _.template('<div><{{ code }}, Message: {{ message }} {% if(file){ %}{{ file.name }}{% } %}</div>')
        , events: {}

        , initialize: function () {
            if(!this.el.id){
                this.$el.attr("id", "FilePicker-"+hashlib.UUID());
                this.$el.find(".btn-upload").attr("id", this.el.id + "-pickfiles");
                this.$fileField = this.$(".data-upload-control");
            }
            var view = this
                    , pathPrefix = hnc.options.staticPrefix
                    , data = this.$el.data()
                    , params = _.extend({
                        runtimes: 'html5,flash,silverlight,gears,html4',
                        browse_button: this.el.id + "-pickfiles",
                        container: this.el.id,
                        max_file_size: '10mb',
                        multi_selection: !data.uploadSingle,
                        flash_swf_url: pathPrefix+'plupload/js/plupload.flash.swf',
                        silverlight_xap_url: pathPrefix+'plupload/js/plupload.silverlight.xap',
                        filters: [{ title: "Pictures", extensions: data.uploadTypes}],
                        url:hnc.options.uploadUrl
                    });

            this.$target = this.options.$target;
            this.uploader = new plupload.Uploader(params);

            this.uploader.bind('Init', function (up, params) {
                view.$el.find('.filelist').html("");
            });
            this.uploader.init();

            this.uploader.bind('FilesAdded', function (up, files) {
                $.each(files, function (i, file) {
                    view.trigger("file:uploadBeforeStart", file);
                    if(!view.options.uploadProgress)
                        view.$el.find('.filelist').append(view.uploading_template(file));
                });
                up.start();
                up.refresh();
            });

            this.uploader.bind('UploadProgress', view.options.uploadProgress || function (up, file) {
                var root = view.$el.find('#' + file.id);
                root.find("b").html(file.percent + "%");
                root.find(".bar").css("width", file.percent + "%")
            });

            this.uploader.bind('Error', function (up, err) {
                view.$el.find('.filelist').append(view.error_template(err));
                up.refresh();
            });

            this.uploader.bind('FileUploaded', function (up, file, xhr) {
                var resp = JSON.parse(xhr.response), file_path = resp.Upload.file;
                view.trigger("file:uploaded", file_path, file);
                view.$el.find('#' + file.id).remove();
            });
        }
    });
    return FileUploadView;
});