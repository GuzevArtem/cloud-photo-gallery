class PhotoReloader {

    constructor(sId, interval) {
        this.elem = $(sId);
        this.interval = interval;
        this.reloadBtn = this.elem.find('.reload_button');

        //depends on photos
        this.removeBtns = this.elem.find('.remove_button');
        this.count = null;
        this.photos = null;
        this.hash = null;
        this.createEvents();
        this.removeButtonsEvents();
    }

    calcPhotosHash() {
        this.photos = this.elem.find('li.preview_image');
        this.count = this.photos.length;
        if (this.count != 0) {
            var ids = [];
            //console.log(this.photos)
            this.photos.each(i => {
                //console.log(this.photos[i]);
                ids.push(this.photos[i].id);
            });
            ids.sort( (a, b) => a - b );
            var bytes = [], str = ''+ids;
            for(var i=0; i<str.length; i++) {
                bytes.push(str.charCodeAt(i));
            }
            //console.log('hashing:', str, this.count);
            this.hash = sha512(bytes);
            return this.hash;
        } else {
            this.hash = -1; //always updates view, but will not causing hash recounting
            return -1;
        }
    }

    getRemote(request_type) {
        if (this.hash == null) this.calcPhotosHash();

        $.ajax({
            type: request_type,
            url: '/photos/reload',
            async: true,
            dataType: "json",
            contentType: 'application/json',
            data: JSON.stringify({
                "count": this.count,
                "hash": this.hash
            }),
            success: (data) => {
                if (data && data.length != 0) {
                    console.log('Updating view...')
                    this.hash = null;
                    this.clear();
                    this.append(data);
                    this.removeBtns = this.elem.find('.remove_button');
                    this.removeButtonsEvents();
                }
            }
        });
    }

    reload(event) {
        if (event != null) event.preventDefault();
        this.getRemote('post');
    }

    forceReload() {
        this.getRemote('get');
    }

    remove(event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        var url = target.attr('value');
        var id = target.parent().attr('id');
        $.ajax({
            type: 'delete',
            url: url,
            async: true,
            success: () => {
                console.log('Updating view...')
                this.elem.find('#' + id).remove();
                this.removeBtns = this.elem.find('.remove_button');
                this.removeButtonsEvents();
            }
        });
    }

    clear() {
        this.elem.children().not('.reload_button').remove();
    }

    rename(id, name) {
        var list_elem = this.elem.find('#' + id);
        if (list_elem == null || list_elem.length != 1) {
            console.warn('Unable to find item to update');
            return;
        }
        list_elem.find('.file_desc').text(name);
    }

    renameRemote(event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        var name = target.attr('value');
        var id = target.parent().attr('id');
        $.ajax({
            type: 'put',
            url: 'photo/'+id,
            async: true,
            dataType: "json",
            contentType: 'application/json',
            data: JSON.stringify({
                "name": name
            }),
            success: () => {
                console.log('Updating view...')
                this.rename(id, name);
            }
        });
    }

    append(photos) {
        if (photos == null || photos.length == 0) {
            this.elem.append("<h2>You haven't any photo yet :(</h2>");
            return;
        }

        /*
        <li class="preview_image" id="{{ image.id }}">
            //...
        </li>
        */
        var list = $('<ol>');
        for (var i = 0; i < photos.length; i++) {
            const photo = photos[i];
            console.log(photo);
            const id = photo.id;
            let li = $('<li>').addClass('preview_image');
            li.attr('id', id);
            //<button class="remove_button" name="" value="{{ url_for('photoRemove', id = image.id) }}">X</button>
            let removeBtn = $('<button>').addClass('remove_button');
            removeBtn.attr('value', photo.removeUrl);
            removeBtn.text('X');
            removeBtn.attr('name', "remove_"+i); 

            //<a class="image" href="{{ url_for('photoDownload', username = current_user.name, id = image.id) }}">
            //   <img src="{{ url_for('photoShowFor', username = current_user.name, id = image.id) }}" height="{{ image.height }}" alt="{{ image.filename }}" />
            //</a>
            let image_download = $('<a>').addClass('image');
            image_download.attr('href', photo.downloadUrl);
            let image = $('<img>')
            image.attr('src', photo.url);
            image.attr('height', photo.height);
            image.attr('alt', photo.filename);
            image_download.append(image);

            //<div>
            //  <p class="file_number">{{ loop.index }}.</p><p class="file_desc"> {{ image.filename }}</p>
            //</div>
            let titleDescriptionDiv = $('<div>');
            let titleDescriptionP1 = $('<p>').addClass('file_number').text(i+1);
            let titleDescriptionP2 = $('<p>').addClass('file_desc').text(photo.filename);
            titleDescriptionDiv.append(titleDescriptionP1);
            titleDescriptionDiv.append(titleDescriptionP2);
            
            li.append(removeBtn);
            li.append(image_download);
            li.append(titleDescriptionDiv);
            list.append(li);
        }
        this.elem.append(list);
    }

    removeButtonsEvents() {
        this.removeBtns.click(this.remove.bind(this));
    }

    createEvents() {
        this.reloadBtn.click(this.forceReload.bind(this));
        setInterval(this.reload.bind(this), this.interval);
    }
}