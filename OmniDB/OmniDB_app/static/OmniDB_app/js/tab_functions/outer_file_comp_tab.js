/**
 * 比较数据库结构文件
 */
var v_createFileCompareTabFunction = function () {
    let v_tab = v_connTabControl.createTab({
        p_icon: '<i class="fas fa-newspaper"></i>',
        p_name: 'Compare Databases',
        p_close: false,
        p_selectable: false,
        p_clickFunction: function(e) {
          showAlert('Compare Databases based on files');
        },
        p_omnidb_tooltip_name: '<h5 class="my-1">Compare Databases based on files</h5>'
      });
}