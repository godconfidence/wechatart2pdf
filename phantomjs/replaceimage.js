window.onload = function change() {
    var metas = document.getElementsByTagName('meta');
    metas[0].insertAdjacentHTML('beforeBegin', "<meta name='referrer' content='never'>");
    var body = document.getElementById("activity-detail");

    //图片请求设置cookie
    body.insertAdjacentHTML("beforeBegin", "<image style='display: none' src='http://mmbiz.qpic.cn/mmbiz_png/pmBoItic0ByggW4X5ACKS5rfIfB1VM7RIic0TA9no7a0pRFHLcBibJX8VAyxUw756hHibQccolNUjRbKviaT3QzpwJA/0?wx_fmt=png' alt='bg'/>");

    //替换img图片链接
    var imglist = body.getElementsByTagName('IMG')
    for (i = 0; i < imglist.length; i++) {
        if (imglist[i].getAttribute('src')!=null && imglist[i].getAttribute('src').length > 0 && imglist[i].getAttribute('src').indexOf("mmbiz.qpic.cn") > -1) {
            imglist[i].setAttribute('src', "http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl=" + imglist[i].getAttribute('src'));
        }

        if (imglist[i].getAttribute('data-src')!=null && imglist[i].getAttribute('data-src').length > 0 && imglist[i].getAttribute('data-src').indexOf("mmbiz.qpic.cn") > -1) {
            imglist[i].setAttribute('src', "http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl=" + imglist[i].getAttribute('data-src'));
        }
		if (imglist[i].getAttribute('data-s')!=null && imglist[i].getAttribute('data-s').length > 0) {
			var w=imglist[i].getAttribute('data-s').split(",")[0];
			var h=imglist[i].getAttribute('data-s').split(",")[1];
            imglist[i].setAttribute('width',h);
			imglist[i].setAttribute('height',w);
        }
      
    }

    //替换背景图片
    var sectionlist = document.querySelectorAll('section')
    for (j = 0; j < sectionlist.length; j++) {
        var newhtml = sectionlist[j].style.backgroundImage.replace("http://mmbiz.qpic.cn", "http://read.html5.qq.com/image?src=forum&q=5&r=0&imgflag=7&imageUrl=http://mmbiz.qpic.cn");
        sectionlist[j].style.backgroundImage = newhtml;
    }
}
