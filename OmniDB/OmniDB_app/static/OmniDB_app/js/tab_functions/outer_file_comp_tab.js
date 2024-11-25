/**
 * 比较数据库结构文件
 */
var v_createFileCompareTabFunction = function () {
    let v_tab = v_connTabControl.createTab({
        p_icon: '<i class="fas fa-newspaper"></i>',
        p_name: 'Compare Databases',
        p_close: false,
        p_selectable: false,
        p_clickFunction: function (e) {
            showAlert('Compare Databases based on files');
        },
        p_omnidb_tooltip_name: '<h5 class="my-1">Compare Databases based on files</h5>'
    });

    v_connTabControl.selectTab(v_tab);

    var v_html =
        '<div style="position: relative;">' +
      '<div style="display: grid; grid-template-areas: \'left right\'; grid-template-columns: auto minmax(0, 1fr);">' +
        '<div id="' + v_tab.id + '_div_left" class="omnidb__workspace__div-left col" style="max-width: 300px; width: 300px;">' +
          "<div class='row'>" +

            // "<div onmousedown='resizeHorizontal(event)' style='width: 10px; height: 100%; cursor: ew-resize; position: absolute; top: 0px; right: 0px;'><div class='resize_line_vertical' style='width: 5px; height: 100%; border-right: 1px dashed #acc4e8;'></div><div style='width:5px;'></div></div>" +

            '<div class="omnidb__workspace__content-left">' +
              '<div id="' + v_tab.id + '_details" class="omnidb__workspace__connection-details"></div>' +
              '<div id="' + v_tab.id + '_tree" style="overflow: auto; flex-grow: 1; transition: scroll 0.3s;"></div>' +
              '<div id="' + v_tab.id + '_left_resize_line_horizontal" class="omnidb__resize-line__container" onmousedown="resizeTreeVertical(event)" style="width: 100%; height: 5px; cursor: ns-resize;"><div class="resize_line_horizontal" style="height: 0px; border-bottom: 1px dashed #acc4e8;"></div><div style="height:5px;"></div></div>' +
              '<div id="tree_tabs_parent_' + v_tab.id + '" class="omnidb__tree-tabs omnidb__tree-tabs--not-in-view" style="position: relative;flex-shrink: 0;flex-basis: 280px;">' +
                '<div id="' + v_tab.id + '_loading" class="div_loading" style="z-index: 1000;">' +
                  '<div class="div_loading_cover"></div>' +
                  '<div class="div_loading_content">' +
                  '  <div class="spinner-border text-primary" style="width: 4rem; height: 4rem;" role="status">' +
                  '    <span class="sr-only ">Loading...</span>' +
                  '  </div>' +
                  '</div>' +
                '</div>' +
                '<button type="button" onclick="toggleTreeTabsContainer(' + "'tree_tabs_parent_" + v_tab.id + "','" + v_tab.id + "_left_resize_line_horizontal'" + ')" class="btn omnidb__theme__btn--secondary omnidb__tree-tabs__toggler"><i class="fas fa-arrows-alt-v"></i></button>' +
                '<div id="tree_tabs_' + v_tab.id + '" class="omnidb__tree-tabs__container" style="position: relative;"></div>' +
              '</div>' +
            '</div>' +
          '</div>' +
          '<div class="resize_line_vertical omnidb__resize-line__container" onmousedown="resizeConnectionHorizontal(event)" style="position:absolute;height: 100%;width: 10px;cursor: ew-resize;border-right: 1px dashed #acc4e8;top: 0px;right: 0px;"></div>' +
        '</div>' +//.div_left
        '<div id="' + v_tab.id + '_div_right" class="omnidb__workspace__div-right col" style="position: relative;">' +
          // "<div class='row'>" +
            '<button type="button" class="py-4 px-0 btn omnidb__theme__btn--secondary omnidb__tree__toggler" onclick="toggleTreeContainer()"><i class="fas fa-arrows-alt-h"></i></button>' +
            '<div id="' + v_tab.id + '_tabs" class="w-100"></div>' +
          // "</div>" +
        '</div>' +//.div_right
      '</div>' +//.row

    '</div>';
}