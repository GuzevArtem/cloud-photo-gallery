(function () {

    var input = document.querySelector(".photo_select"),
        preview = document.querySelector(".photo_preview"),
        resetButton = document.querySelector(".photo_selector button.reset")
        ;


    function returnFileSize(number) {
        if (number < 1024) {
            return number + 'bytes';
        } else if (number > 1024 && number < 1048576) {
            return (number / 1024).toFixed(1) + 'KB';
        } else if (number > 1048576) {
            return (number / 1048576).toFixed(1) + 'MB';
        }
    }

    function validFileType(file) {
        var fileTypes = [
            'image/jpg',
            'image/jpeg',
            'image/pjpeg',
            'image/png'
        ]

        for (var i = 0; i < fileTypes.length; i++) {
            if (file.type === fileTypes[i]) {
                return true;
            }
        }

        return false;
    }

    function updateImageDisplay() {
        while (preview.firstChild) {
            preview.removeChild(preview.firstChild);
        }

        var curFiles = input.files;
        if (curFiles.length === 0) {
            var para = document.createElement('h1');
            para.innerText = 'No files currently selected for upload';
            preview.appendChild(para);
        } else {
            var list = document.createElement('ol');
            preview.appendChild(list);
            for (var i = 0; i < curFiles.length; i++) {
                var listItem = document.createElement('li');
                listItem.classList.add('preview_image');

                var div_file_desc = document.createElement('div');
                var number = document.createElement('p');
                number.classList.add('file_number');
                number.textContent = (i+1) + '.';
                
                var file_desc = document.createElement('p');
                file_desc.classList.add('file_desc');

                div_file_desc.appendChild(number);
                div_file_desc.appendChild(file_desc);
                if (validFileType(curFiles[i])) {
                    file_desc.textContent = ' ' + curFiles[i].name + ', ' + returnFileSize(curFiles[i].size) + '.';
                    var image = document.createElement('img');
                    image.src = window.URL.createObjectURL(curFiles[i]);

                    listItem.appendChild(image);

                } else {
                    file_desc.textContent = ' ' + curFiles[i].name + ': Not a valid file type.';

                }
                listItem.appendChild(div_file_desc);
                list.appendChild(listItem);
            }
        }
    }

    function displayDefultMesage() {
        while (preview.firstChild) {
            preview.removeChild(preview.firstChild);
        }
        var para = document.createElement('h1');
            para.innerText = 'No files currently selected for upload';
            preview.appendChild(para);
    }

    resetButton.onclick = displayDefultMesage;
    input.onchange = updateImageDisplay;
    displayDefultMesage();   //display default value

}());