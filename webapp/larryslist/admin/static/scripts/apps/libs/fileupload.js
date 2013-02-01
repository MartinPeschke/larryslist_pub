define(["tools/hash", "plupload"], function (hashlib) {

var FileUploadView = Backbone.View.extend({
        uploading_template:
                    _.template('<div id="{{ id }}" class="upload-progress"><b>0%</b> {{ name }} ({{ (size/1024).toFixed(0) }}K)<div class="progress"><div class="bar"></div></div></div>')
        , error_template: _.template('<div><{{ code }}, Message: {{ message }} {% if(file){ %}{{ file.name }}{% } %}</div>')
        , events: {}

        , initialize: function (opts) {
            this.$button = this.$el.find(".btn-upload");
            if(!this.el.id){
                this.$el.attr("id", "FilePicker-"+hashlib.UUID());
                this.$button.attr("id", this.el.id + "-pickfiles");
                this.$fileField = this.$(".data-upload-control");
            }
            var data = this.$el.data();
            if(data.fileTypes)this.buildUploader(opts, this.el.id, data);
        }
        , buildUploader: function(opts, rootId, data){
                var pathPrefix = hnc.options.staticPrefix
                    , uploadUrl = hnc.options.uploadUrl

                    , params = _.extend({
                        runtimes: 'html5,flash,silverlight,gears,html4',
                        browse_button: this.$button.attr("id"),
                        container: rootId,
                        max_file_size: '10mb',
                        multi_selection: !data.uploadSingle,
                        flash_swf_url: pathPrefix+'plupload/js/plupload.flash.swf',
                        silverlight_xap_url: pathPrefix+'plupload/js/plupload.silverlight.xap',
                        filters: [{ title: "Files", extensions: data.fileTypes}],
                        url:uploadUrl
                });
                this.$target = opts.$target;
                this.uploader = new plupload.Uploader(params);
                this.uploader.bind('Init', this.onUploaderInit, this);
                this.uploader.init();
                this.uploader.bind('FilesAdded', this.onFilesAdded, this);
                this.uploader.bind('UploadProgress', opts.uploadProgress || this.onProgress, this);
                this.uploader.bind('Error', this.onError, this);
                this.uploader.bind('FileUploaded', this.onFileUploaded, this);
        }
        , destroy: function(){
            this.uploader&&this.uploader.destroy();
            this.$el.off();
        }
        , onUploaderInit: function(){
            this.$el.find('.filelist').html("");
        }
        , onFilesAdded: function(up, files){
            var view = this;
            $.each(files, function (i, file) {
                view.trigger("file:uploadBeforeStart", file);
                if(!view.options.uploadProgress)
                    view.$el.find('.filelist').append(view.uploading_template(file));
            });
            up.start();
            up.refresh();
        }
        , onProgress: function(up, file){
            var root = this.$el.find('#' + file.id);
            root.find("b").html(file.percent + "%");
            root.find(".bar").css("width", file.percent + "%")
        }
        , onError: function(up, err){
            this.$el.find('.filelist').append(this.error_template(err));
            up.refresh();
        }
        , onFileUploaded: function(up, file, xhr){
            var resp = JSON.parse(xhr.response), file_path = resp.Upload.file;
            this.trigger("file:uploaded", file_path, file);
            this.$el.find('#' + file.id).remove();
        }
    });
    return FileUploadView;
});