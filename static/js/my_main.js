var image_domain = ''
if (window.location.port != 10003){
    image_domain=window.location.href.indexOf('172.99') > -1? 'http://172.99.128.18:8888/': 'http://10.4.14.66:8888/';
}
else{
  image_domain = ('http://' + window.location.hostname + ":10004/")
}




function getHMS(timestamp) {
  let time = new Date(timestamp);
  let year = time.getFullYear();
  const month = (time.getMonth() + 1).toString().padStart(2, '0');
  const date = (time.getDate()).toString().padStart(2, '0');
  const hours = (time.getHours()).toString().padStart(2, '0');
  const minute = (time.getMinutes()).toString().padStart(2, '0');
  const second = (time.getSeconds()).toString().padStart(2, '0');
  return hours + ':' + minute + ':' + second;
}

function show_msg(content) {
  var d = dialog({
    content: content
  });
  d.show();
  setTimeout(function () {
    d.close().remove();
  }, 1200);

}

COLOR_CONFIG = {1:'黄', 2:'蓝', 3:'黑', 5:'白', 6:'绿', 7:'黄绿', 9:'其他'}
event_type = '';
event_type_cn = '';

function get_item_detail_html(item_data, with_div = true) {
  var id = item_data['id'];
  var cam_id = item_data['cam_id'];
  var cam_data = item_data['cam_data'];
  var cam_lat = item_data['cam_latitude'];
  var cam_lng = item_data['cam_longitude'];

  var cam_name = item_data['cam_name'];
  var event_data = item_data['event_data'];
  var event_time = event_data['time'].split(".")[0];
  var event_pic_path = event_data['picpath'];
  var plate_info =''
  var plate_color_info = ''
  //var _event_type =
  try{
     plate_info = JSON.parse(event_data['platelicense'])[0];
     plate_color_info = COLOR_CONFIG[Number(event_data['platecolor'] || '0')] || '未识别'
  }
  catch (e) {
    plate_info = ''
    plate_color_info = '未识别'
  }


  var verify_status = item_data['verify_status'];
  var verify_status_cn = item_data['verify_status_cn']
  var label_class = 'label-default'
  if(event_pic_path!=null&&event_pic_path){
    var real_img_path = image_domain + event_pic_path.replace(".jpg","_250x250.jpg");
  }
  else {
    var real_img_path = "/static/imgs/noimg2.png"
  }

  if (verify_status == 1) {
    label_class = 'label-danger'
  } else if (verify_status == 2) {
    label_class = 'label-warning'
  }
  var inner_html = '                <img style="width: 100%;height: 181px" src="' + real_img_path + '" ' +
      '                   onclick="go_detail(' + id + ')">\n' +
      '                <div style="padding-top: 10px;text-align: center">\n' +
      '                    <div>' + cam_name + '</div> ' +
      '                    <div style="margin-bottom: 3px">' + event_time + (event_type=='vehicleillegalstop'? '&nbsp;车牌:'+ plate_info:'') + (event_type=='vehicleillegalstop'? '车牌色:'+ plate_color_info:'') + '&nbsp;<span class="label  ' + label_class + '">' + verify_status_cn + '</span></div> ' +
      '                    <button class="btn btn-small  btn-danger" type="button" onclick="verify(' + id + ',1)"> 上报 </button>\n' +
      '                    <button class="btn btn-small  btn-info" type="button" onclick="verify(' + id + ',2)"> 标记为误判 </button>\n' +
      '                </div>\n'

  if (with_div) {
    inner_html = '            <div class="col-sm-3" style="margin-top: 8px" id="' + id + '">\n' +
        inner_html +
        '            </div>'

  }
  return inner_html
}


function init_list(page = 1) {
  jQuery.post({
    url: "/get_event_items",
    data: {
      "event_type": event_type,
      'page': page,
      'num': 12
    },
    success: function (res) {
      console.log(res)
      var total_count = res['total_count'];
      var total_page = res['total_page'];
      var data = res['data'];
      //var page = res['page'];
      var html = '';
      var pagi_html = '';
      var page_range = res['page_range'];
      Object.entries(data).forEach(function (item) {
            var _index = item[0];
            var item_data = item[1];
            //console.log(item)
            html += get_item_detail_html(item_data);
          }
      )

      Object.entries(page_range).forEach(function (item) {
        var num = item[1];
        if (num == page) {
          pagi_html += '<li class="active" onclick="init_list(' + num + ')"><a href="#">' + num + '</a></li>'
        } else {
          pagi_html += '<li  onclick="init_list(' + num + ')"><a href="#">' + num + '</a></li>'
        }

      })
      jQuery("#main-content").html(html);
      jQuery('#pagi-content').html(pagi_html);
    }
  })
  return true;

}


function go_detail(id) {
  //console.log(rtsp)
  jQuery.post({
    url: "/get_event_item",
    data: {"id": id},
    success: function (res) {
      var image_url = res['event_data']['picpath'] || '';
      var event_data = res['event_data'];

      var plate_info =''
      var plate_color_info = ''
      try{
         plate_info = JSON.parse(event_data['platelicense'])[0];
         plate_color_info = COLOR_CONFIG[Number(event_data['platecolor'] || '0')] || '未识别'
      }
      catch (e) {
        plate_info = ''
      }

      //console.log(res);
      //console.log(image_url)
      var detail_dialog = dialog({
        width: 800,
        height: 560,
        title: '图片详情',

        content: '<div style="width: 100%;"><img  style="width: 100%" src="' + image_domain + image_url + '">' +
            '<p style="text-align: center">' + (event_type=='vehicleillegalstop'? '&nbsp;车牌:'+ plate_info:'') + '</p>' +
            '<p style="text-align: center">' + (event_type=='vehicleillegalstop'? '&nbsp;车牌颜色:'+ plate_color_info:'') + '</p>'  +
            '</div>'
      });
      //detail_dialog.showModal();
      detail_dialog.show();
    }

  })

  //jQuery.get
  //detail_dialog.show();

}

function verify(id, status) {
  jQuery.post({
    url: "/get_event_item",
    data: {"id": id},
    success: function (res) {
      var image_url = res['event_data']['picpath'] || '';
      var cam_name = res['cam_name'];
      var event_data = res['event_data'];
      var event_time = event_data['time'];
      //console.log(res);
      console.log(image_url)
      var detail_dialog = dialog({
        width: 700,
        height: 560,
        title: status == 1 ? '确定要上报事件么？' : '确定要标记为程序误判么',
        okValue: status == 1 ? '上报' : '标记误判',
        content: '<div style="width: 100%;">' +
            '<p>' + cam_name + '</p>' +
            '<p>' + event_time + '</p>' +
            '<img  style="width: 100%" src="' +  image_domain + image_url + '"></div>',

        ok: function () {
          jQuery.post({
            url: "/verify_event",
            data: {id: id, verify_status: status},
            success: function (res) {
              var msg = res['message'];
              var _status = res['status'];
              var data = res['data'];
              if (!_status) {
                show_msg(msg)
              } else {
                show_msg(msg);

              }
              refresh_item(id);
            }
          })
          return true;
        },
        cancelValue: '取消',
        cancel: function () {
        }
      });
      detail_dialog.showModal();

    }
  })
}

function refresh_item(id) {
  jQuery.post({
    url: "/get_event_item",
    data: {"id": id},
    success: function (res) {
      var item_data = res;
      var html_info = get_item_detail_html(item_data,false);
      jQuery("#"+id).html(html_info)
      //console.log(res);

    }
  })
}

$(document).ready(function () {
      init_list()
    }
)