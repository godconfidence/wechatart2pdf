var page = require('webpage').create();
var system = require('system');
var fs = require('fs');

phantom.outputEncoding = 'gb2312';


page.onError = function (msg, trace) {
    console.log(msg);
    var msgStack = ['PHANTOM ERROR: ' + msg];
    if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function (t) {
            msgStack.push(' -> ' +
                (t.file || t.sourceURL) + ': ' + t.line +
                (t.function ? ' (in function ' + t.function + ')' : ''));
        });
    }
    console.error(msgStack.join('\n'));
    phantom.exit(1);
};

if (system.args.length == 1) {
    console.log('请输入文章地址');
    phantom.exit();
} else {

    var url = system.args[1];
    var filename = '';
	var short_dic_path='';
	
    if (system.args.length == 3) {
        filename = system.args[2];
    }
	
	if (system.args.length == 4) {
        filename = system.args[2];
		short_dic_path = system.args[3];
    }

    //地址检测
    if (url.indexOf('http') == -1) {
        url = 'http://' + url;
    }

    page.viewportSize = { width: 600, height: 20 };//设置图片大小 height自动适应

    //================================pdf页面设置================================
    page.settings.userAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36';
    //page.zoomFactor = 1;//页面缩放比例
    page.settings.loadImages = true;//页面加载图片

    //format ：A4 纸，可以设置 "5in*7.5in", "10cm*20cm",  "Letter" 等
    //orientation ：纸方向是竖着的，或者 landscape
    //margin ：与纸四边间距，可自定义，也可详细设置 margin : { left: ‘0.8cm‘,  top : ‘0.8cm‘,  right : ‘0.8cm‘,  bottom : ‘0.8cm‘ }
    //设置页面格式
    //page.paperSize = { format: 'A4', orientation: 'portrait', margin: '0.8cm' };
	page.paperSize = {
        format: 'A4',
        orientation: 'portrait',
        margin: {
            left: '0.8cm', top: '0.8cm', right: '0.8cm', bottom: '0.1cm'
        }
    };
    //================================pdf页面设置================================

    page.open(url, function (status) {//加载页面
        console.log('抓取结果:' + status);

        var title = page.evaluate(function () {
            return document.title;
        });
		console.log(title);
        var title = title
            .replace('|', '').replace('\\', '').replace('/', '').replace(':', '').replace('*', '')
            .replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('&nbsp;', ' ');

        filename = filename.length > 0 ? filename : title;

        var wait = 20;
        //是否是微信地址
        if (url.indexOf("mp.weixin.qq.com") > -1) {

            wait = 5000;
            //加载微信图片
            //includeJs 侧重网络js文件，尤其在引入jQuery等第三方库
            //injectJs 侧重本地的js文件，与libraryPath挂购
            page.injectJs('replaceimage.js', function () {
                var titlexx = page.evaluate(function () {
                    return document.title;
                });
            });
            //console.log(title);
            console.log('等待5秒生成pdf');
        }

        //等待页面执行完js后在进行生成
        window.setTimeout(function () {
            page.render(filename + '.pdf');
            console.log('pdf生成成功:' + title);
            phantom.exit();
        }, wait);

    });
}
