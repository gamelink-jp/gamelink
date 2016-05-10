#!/usr/bin/perl
# フォームからデータを取得する

use CGI;

#####
# form データ取得

sub get_data {
  $q = new CGI;
  $who = $q->param('who');
  $maker_name = $q->param('maker_name');
  $maker_name2 = $q->param('maker_name2');
  $url = $q->param('url');
  $b_url = $q->param('b_url');
  $width = $q->param('width');
  $height = $q->param('height');
  $comment = $q->param('comment');
  $user_name = $q->param('user_name');
  $u_mail_ad = $q->param('u_mail_ad');
}

1;
