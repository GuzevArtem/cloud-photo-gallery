
class UPSender {

    constructor(sId) {
        this.elem = $(sId);
        this.url = this.elem.attr("action");
        this.error_msg = this.elem.find(".error");
        this.u = this.elem.find(".username");
        this.p = this.elem.find(".password");
        this.r = this.elem.find(".remember");


        this.createEvents();
    }

    getRemote(event) {
        event.preventDefault();
        //console.log("[POST]", this.url, this.u.val(), sha512(this.p.val()), this.r.is(':checked') ? 'on' : 'off')
        $.ajax({
            type: 'post',
            url: this.url,
            async: true,
            dataType: "json",
            contentType: 'application/json',
            data: JSON.stringify({
                "username": this.u.val(),
                "password": sha512(this.p.val()),
                "remember": this.r.is(':checked') ? 'on' : 'off'
            }),
            success: (data) => {
                console.log(data)
                if (data) {
                    window.location.href = data.href;
                }
            }
        }).fail((xhr, status, error) => {
            console.error(status);
            let error_message = null;
            if (xhr.responseJSON != null) {
                error_message = xhr.responseJSON['error_msg'];
            }
            this.error_msg.text(error_message == null ? '500 Try again later' : error_message);
        });
    }

    createEvents(){
		this.elem.submit(this.getRemote.bind(this))
	}

}