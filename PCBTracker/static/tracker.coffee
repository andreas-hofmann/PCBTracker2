$ ->
  g_speed = 250

  navigate = (target) ->
    _parent = $('.nav-button[id="' + target + '"]').parent('li')

    $('li.dropdown').removeClass 'active'
    $('a.nav-button').each ->
      $(this).parent('li').removeClass 'active'

    baseurl = '/'

    _parent.addClass 'active'
    $('#main').animate { opacity: 0.00 }, g_speed, ->
      $('#main').load baseurl + encodeURIComponent(target), null, (response, status, xhr) ->
        $('#main').animate { opacity: 1.00 }, g_speed

        if status == 'error'
          $('#main').html '<div class=\'error\'>Error: ' + xhr.status + ': ' + xhr.statusText
          return


  show_patch_popup = (data) ->
    board = data.board_id
    patch = data.patch_id
    latest_rev = data.latest_rev
    patch_name = data.patch_name
    patch_desc = data.patch_desc
    board_name = data.board_name
    lowest_rev = 1
    popup = $('<div></div>')
    if !latest_rev
      latest_rev = 0
      lowest_rev = 0
    popup.dialog
      'modal': true
      'title': 'Updating patch for ' + board_name
      'close': ->
        $(this).dialog('destroy').remove()
        return
      'position':
        my: 'left-35 top+25'
        of: '#b' + board + '_p' + patch
      'buttons':
        'Apply patch': ->
          commit_patchstatus board patch $('#revisiondropdown').val()
          return
        'Remove patch': ->
          $(this).dialog 'close'
          commit_patchstatus board  patch  '-'
          return
    popup.append 'Editing patch \'' + patch_name + '\'<br>'
    popup.append 'Set revision\n<select id=\'revisiondropdown\'>\n</select>'
    i = latest_rev
    while i >= lowest_rev
      $('#revisiondropdown').append '<option value=\'' + i + '\'>' + i + '</option>'
      --i
    return


  update_patch_status = (board_id, patch_id) =>
    $.ajax
      url: '/update_patch_status'
      type: 'POST'
      data: { 'board_id': board_id, 'patch_id': patch_id }
      success: (data) ->
        if data
          show_patch_popup data
      error: (error) ->
        console.log error

  commmit_patch_status = (board_id, patch_id, status) =>
    $.ajax
      url: '/commit_patch_status'
      type: 'POST'
      data: { 'board_id': board_id, 'patch_id': patch_id, 'status': status }
      error: (error) ->
        console.log error


  #$(document).ready ->
  #  $('a.nav-button').each ->
  #    $(this).click ->
  #      navigate $(this).attr('id')
  #  navigate "index/"

# vim: ts=2 sw=2 et
