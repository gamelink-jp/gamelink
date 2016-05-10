#!/usr/bin/perl
#
######################################################################
###
###
###  CGIカウンター TcounT Ver.5.03
###     [2/2] 管理 (tcpadm.cgi)
###                                 (c) 1996-2004 Takahiro Nishida
###                                 http://www.mytools.net/
###
###
######################################################################
#
### 変数設定部 （詳細は上記ページをご覧下さい） ######################

# 管理パスワード
$password = "yt112";
# 管理者メールアドレス
$admin_email = "info\@gamelink.jp";
# データファイルの格納位置
$basedir = ".";
# 「戻る」を押したときに移動するURL
$backurl = "http://www.gamelink.jp/";

### 変数設定部 （ここまで）###########################################

# ログ閲覧にパスワードを要するか（1→必要、0→不必要）
$NEED_PASSWORD_FOR_LOGVIEW = 0;
# 「最近×日間の集計」を何日分にする
$RECENT_DAYS_COUNT = 7;
# カウント開始直後の×日を統計対象から除外する
$AVG_IGNORE_DAYS_COUNT = 1;


$lockfile = "$basedir/lockdir/tc.lock";
$allfile = "$basedir/tcdall.txt";
$ystfile = "$basedir/tcdyst.txt";
$hstfile = "$basedir/tcdhst.txt";
$logfile = "$basedir/tcdlog.txt";
$bakfile = "$basedir/tcdbak.txt";

$verno = "5.03";

print "Content-type: text/html; Charset=shift_jis\n\n";

&main;

sub main{
	&lock;
	&init_variables;
	&open_datafile;
	&check_input;
	&exec_action;
	&update_files;
	&show_html;
	&unlock;
}



########## 変数の初期化
sub init_variables{
	$noact = "何も変更されませんでした。";
	$actmsg = "";
	
}



########## データファイルのオープン
sub open_datafile{
	&openfile($allfile, *tdys);
	&openfile($ystfile, *ysts);
	
	### 日付データ取得
	$g_date_rec = shift(@tdys);
	### 取得できなかったらrecoverで一旦初期化
	($g_date_rec) || &error(391, "先に <A HREF=\"./tc.cgi?hoge\">こちら</A> をクリックしてデータファイルの初期化を行い、再度 <A HREF=\"./tcpadm.cgi\">tcpadm.cgi</A> にアクセスしてください。");
	
	### 今日データのハッシュ化
	foreach(@tdys){
		(/^\w+\t/) || next;
		($b_ccode) = split("\t");
		($b_ccode =~ /^\w+/) || next;
		$CTDY{$b_ccode} = $_;
		### ソート順取得
		push(@g_codesort, $b_ccode);
	}
	
	### 昨日データのハッシュ化
	foreach(@ysts){
		($b_ccode) = split("\t");
		($CYST{$b_ccode} = $_);
	}
	
	### 今日のカウント数
	foreach (@g_codesort){
		($b_ccode, $b_ca, $b_cah) = split("\t", $CTDY{$_});
		($b_ccode, $b_cy, $b_cyh, $b_cu, $b_cuh) = split("\t", $CYST{$_});
		
		### 今日＝総合－昨日迄
		$CCT{$_} = $b_ca - $b_cu;
		$CCTH{$_} = $b_cah - $b_cuh;
	}
}



########## 入力内容のチェック
sub check_input{
	local($buffer, $vn, $pair, @pairs);
	
	if ($ENV{'REQUEST_METHOD'} eq "POST") {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	}
	else {
		$buffer = $ENV{'QUERY_STRING'};
	}
	@pairs = split(/&/, $buffer);
	foreach $pair (@pairs) {
		($vn, $value) = split(/=/, $pair);
		$F{$vn} .= $value;
	}
	
	$m_pwd = $F{'pwd'};
	$m_mode = $F{'mode'};
	$m_act = $F{'act'};
	$m_ccode = $F{'ccode'};
	(!$m_ccode) || ($m_ccode =~ /^\w+$/) || &error(300, "カウンターのコード名が不正です：$m_ccode");
}



########## 作業の実行
sub exec_action{
	### パスワードチェック
	if ($m_pwd ne $password){
		$actmsg = ($m_pwd) ? "パスワードが間違っています。$noact" : "作業を選択し、パスワードを入力して「作業実行」を押してください。";
		### logモードかつPassword不要「でない」場合はモードをtopに戻す
		($m_mode eq 'log') && ($NEED_PASSWORD_FOR_LOGVIEW == 0) || ($m_mode = "top");
	}
	
	### modeごとの処理へ
	if($m_mode eq 'cnt'){
		$actmsg = "カウンタ修正用フォームを表\示しています。";
		if($m_act eq 'new' || $m_act eq 'fix'){
			&fix_data;
		}
	}
	elsif($m_mode eq 'log'){
		$actmsg = "カウンターログを表\示しています。";
	}
	elsif($m_mode eq 'clm'){
		&clear_actlog;
		$actmsg = "カウンター動作ログをクリアしました。";
	}
}



########## データの修正
sub fix_data{
	local($m_ccode, $m_cdel);
	local($m_ca, $m_cah, $m_cy, $m_cyh, $m_cu, $m_cuh);
	local($newtdys, $newysts);
	
	### 入力の受け取り
	$m_ccode = $F{'ccode'};
	$m_ca = $F{'ca'};
	$m_cu = $F{'cu'};
	$m_cy = $F{'cy'};
	$m_cah = $F{'cah'};
	$m_cuh = $F{'cuh'};
	$m_cyh = $F{'cyh'};
	$m_cdel = ($F{'cdel'}) ? 1 : 0;
	
	### 入力のチェック
	($m_ccode =~ /^\w+$/) || &error(300, "カウンターコードが不正です：使用できる文字は [A-Za-z0-9] です");
	($m_ca =~ /^\d+$/) || &error(301, "入力が不正です：「述べアクセス数－現在」は半角数字で記入");
	($m_cu =~ /^\d+$/) || &error(302, "入力が不正です：「述べアクセス数－昨日まで」は半角数字で記入");
	($m_cy =~ /^\d+$/) || &error(303, "入力が不正です：「述べアクセス数－昨日」は半角数字で記入");
	($m_cah =~ /^\d+$/) || &error(304, "入力が不正です：「ホストアクセス数－現在」は半角数字で記入");
	($m_cuh =~ /^\d+$/) || &error(305, "入力が不正です：「ホストアクセス数－昨日まで」は半角数字で記入");
	($m_cyh =~ /^\d+$/) || &error(306, "入力が不正です：「ホストアクセス数－昨日」は半角数字で記入");
	
	### 社会的エラー
	($m_ca >= $m_cu) || &error(307, "数値が不正です：延べアクセス数－現在($m_ca)が昨日まで($m_cu)より小さい");
	($m_cu >= $m_cy) || &error(309, "数値が不正です：延べアクセス数－昨日まで($m_cu)が昨日($m_cy)より小さい");
	($m_cah >= $m_cuh) || &error(308, "数値が不正です：ホストアクセス数－現在($m_cah)が昨日まで($m_cuh)より小さい");
	($m_cuh >= $m_cyh) || &error(310, "数値が不正です：ホストアクセス数－昨日まで($m_cuh)が昨日($m_cyh)より小さい");
	
	### 新規
	if($m_act eq 'new')
	{
		($m_ccode) || &error(311, "カウンターコードが入力されていません。");
		($CTDY{$m_ccode}) && &error(312, "指定されたカウンタコードは既に使用されています：$m_ccode");
		$actmsg = "カウンタ $m_ccode を新規作成しました。";
		push(@g_codesort, $m_ccode);
		$F{'cread'} = 0;
	}
	### 修正
	else{
		($CTDY{$m_ccode}) || &error(313, "指定されたカウンタコードは存在しません：$m_ccode");
		$actmsg = "カウンタ $m_ccode を修正しました。";
		$F{'cread'} = 1;
		### 削除
		if($m_cdel)
		{
			foreach(0..$#g_codesort)
			{
				($g_codesort[$_] eq $m_ccode) && splice(@g_codesort, $_, 1);
			}
			$actmsg = "カウンタ $m_ccode を削除しました。";
			$F{'cread'} = 0;
		}
	}
	### ハッシュ作成 or 上書き
	$CTDY{$m_ccode} = "$m_ccode\t$m_ca\t$m_cah\t\n";
	$CYST{$m_ccode} = "$m_ccode\t$m_cy\t$m_cyh\t$m_cu\t$m_cuh\t\n";
	
	### 今日＝総合－昨日迄
	$CCT{$m_ccode} = $m_ca - $m_cu;
	$CCTH{$m_ccode} = $m_cah - $m_cuh;
	
	### データ再編成
	push(@newtdys, $g_date_rec); # 日付
	foreach(@g_codesort)
	{
		### 行挿入
		push(@newtdys, $CTDY{$_});
		push(@newysts, $CYST{$_});
	}
	@tdys = @newtdys;
	@ysts = @newysts;
	
	### 更新フラグ
	$upf_tdys = 1;
	$upf_ysts = 1;
}



########## カウンター動作ログのクリア
sub clear_actlog{
	local @tmps = ();
	&updatefile($logfile, *tmps);
}



########## ファイルの更新
sub update_files{
	($upf_tdys) && &updatefile($allfile, *tdys);
	($upf_ysts) && &updatefile($ystfile, *ysts);
}



########## 表示
sub show_html{
	local($hbuf_copyright, $hbuf_table, $hbuf_form);
	
	($F{'back'}) && ($m_mode = "top");
	
	if($m_mode eq 'cnt'){
		$hbuf_table = &html_table;
		$hbuf_form = &html_form;
	}
	elsif($m_mode eq 'log'){
		$hbuf_table = &html_log;
	}
	else{
		$hbuf_form = &html_top;
	}
	
	$hbuf_copyright = &copyright;
	
	print <<EOP
	<HTML>
	<HEAD>
	<TITLE>T-Count 5 - 管理用ページ</TITLE>
	<STYLE TYPE=\"text/css\">
	<!--
	A{ text-decoration:none; }
	TD{ font-size:12px; text-align:center; }
	TH{ font-size:12px; text-align:center; font-weight:bold; }
	TD.head{ color:#000000; background-color:#FFFFCC; text-align:center; font-weight:bold; }
	TD.form{ color:#000000; background-color:#FFFFFF; }
	TD.comm{ color:#000000; background-color:#FFFFCC; text-align:left; }
	CAPTION{ font-size:13px; text-align:left; }
	
	TH.key{ font-size:12px; font-weight:bold; color:#FFFFFF; background-color:#660000; }
	.attention{ font-size:11px; }
	
	.d { color:#000000; }
	.dh{ color:#0000AA; }
	.dd{ font-size:10px; color:#555555; }
	.u { color:#000000; }
	.uh{ color:#0000AA; }
	.weak { font-size:11px; color:#FF3300; }
	.emp { color:#FF0000; font-weight:bold; }
	
	.w0 { color:#000000; background-color:#FFCCCC; }
	.w1 { color:#000000; background-color:#FFFFFF; }
	.w2 { color:#000000; background-color:#FFFFFF; }
	.w3 { color:#000000; background-color:#FFFFFF; }
	.w4 { color:#000000; background-color:#FFFFFF; }
	.w5 { color:#000000; background-color:#FFFFFF; }
	.w6 { color:#000000; background-color:#CCCCFF; }
	.ws { color:#000000; background-color:#CCFFCC; }
	.m { color:#000000; background-color:#FFFF99; font-weight:bold; }
	
	-->
	</STYLE>
	</HEAD>
	<BODY BGCOLOR=\"#FF9999\">
	<FONT SIZE=\"2\">
	[<A HREF=\"$backurl\">戻る</A>]
	[<A HREF=\"tcpadm.cgi\">管理トップ</A>]
	
	<H3>T-Count 5 管理用ページ</H3>
	<HR SIZE=\"1\" NOSHADE>
	<B>作業状況：</B> $actmsg
	<HR SIZE=\"1\" NOSHADE>
	$hbuf_form
	$hbuf_table
	<HR SIZE=\"1\" NOSHADE>
	<DIV ALIGN=\"right\">$hbuf_copyright</DIV>
	</BODY>
	</HTML>
EOP
}



########## トップ画面
sub html_top{
	local($hbuf_logview);
	
	($NEED_PASSWORD_FOR_LOGVIEW == 0) && ($hbuf_logview = "<SPAN CLASS=\"weak\">※パスワード不要※</SPAN>");
	
	"
	<FORM METHOD=\"post\" ACTION=\"tcpadm.cgi\">
	パスワード<INPUT TYPE=\"password\" NAME=\"pwd\" SIZE=\"15\" VALUE=\"$m_pwd\">
	<INPUT TYPE=\"submit\" VALUE=\"作業実行\"><BR>
	<INPUT TYPE=\"radio\" NAME=\"mode\" VALUE=\"log\" CHECKED>カウンタログ、動作ログ閲覧&nbsp;&nbsp;$hbuf_logview<BR>
	<INPUT TYPE=\"radio\" NAME=\"mode\" VALUE=\"cnt\">カウンタ新規作成、修正、削除<BR>
	<INPUT TYPE=\"radio\" NAME=\"mode\" VALUE=\"clm\">動作ログのクリア<BR>
	</FORM>
	";
}



########## 修正用フォーム
sub html_form{
	local($b_ccode, $b_ca, $b_cah);
	local($b_ccode, $b_cy, $b_cyh, $b_cu, $b_cuh);
	
	### プルダウン
	foreach(@g_codesort)
	{
		($b_selected) = ($_ eq $m_ccode) ? "SELECTED" : "";
		$hbuf_options .= "<OPTION " . $b_selected . ">" . $_ . "\n";
	}
	
	### 読み込みの場合
	if($F{'cread'})
	{
		($m_ccode) || &error(8, "コードが指定されていません");
		($b_ccode, $b_ca, $b_cah) = split("\t", $CTDY{$m_ccode});
		($b_ccode, $b_cy, $b_cyh, $b_cu, $b_cuh) = split("\t", $CYST{$m_ccode});
		$b_act = "fix";
		$b_title = "$m_ccode 修正";
		$hbuf_ccode = "<INPUT TYPE=\"hidden\" NAME=\"ccode\" VALUE=\"$m_ccode\">$m_ccode &nbsp;&nbsp;&nbsp;<SPAN CLASS=\"weak\">（※変更不可※）</SPAN>";
		$hbuf_del = "<INPUT TYPE=\"checkbox\" NAME=\"cdel\" VALUE=\"1\">このカウンタを削除&nbsp;&nbsp;&nbsp;";
	}
	### 新規作成の場合
	else
	{
		($b_ca, $b_cah, $b_cy, $b_cyh, $b_cu, $b_cuh) = (0, 0, 0, 0, 0, 0);
		$b_act = "new";
		$b_title = "新規登録";
		$hbuf_ccode = "<INPUT TYPE=\"text\" NAME=\"ccode\" SIZE=\"15\">&nbsp;&nbsp;&nbsp;<SPAN CLASS=\"weak\">（※半角英数字※）</SPAN>";
	}
	
	$htmlbuf .= "
		<FORM METHOD=\"post\" ACTION=\"tcpadm.cgi\">
		<INPUT TYPE=\"hidden\" NAME=\"pwd\" VALUE=\"$m_pwd\">
		<INPUT TYPE=\"hidden\" NAME=\"mode\" VALUE=\"cnt\">
		<DIV ALIGN=\"center\">
		<TABLE WIDTH=\"70%\" BORDER=\"1\" CELLPADDING=\"1\" CELLSPACING=\"0\" BGCOLOR=\"#FFFFFF\">
		<TR><TH CLASS=\"key\">
		カウンタ
		<SELECT NAME=\"ccode\" SIZE=\"1\">
		$hbuf_options
		</SELECT>
		を
		<INPUT TYPE=\"submit\" NAME=\"cread\" VALUE=\"読み込み\"> or 
		<INPUT TYPE=\"submit\" NAME=\"cnew\" VALUE=\"新規登録\">
		&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
		<INPUT TYPE=\"submit\" NAME=\"back\" VALUE=\"↑戻る\">
		</FONT></TD></TR></TABLE>
		</DIV>
		</FORM>
		<P>
	";
	
	$htmlbuf .= "
		<FORM METHOD=\"post\" ACTION=\"tcpadm.cgi\">
		<INPUT TYPE=\"hidden\" NAME=\"pwd\" VALUE=\"$m_pwd\">
		<INPUT TYPE=\"hidden\" NAME=\"mode\" VALUE=\"cnt\">
		<INPUT TYPE=\"hidden\" NAME=\"act\" VALUE=\"$b_act\">
		<DIV ALIGN=\"center\">
		<TABLE WIDTH=\"80%\" BORDER=\"1\" CELLPADDING=\"1\" CELLSPACING=\"0\" BGCOLOR=\"#FFFFFF\">
		<TR><TH CLASS=\"key\" COLSPAN=\"2\"><FONT COLOR=\"#FFFFFF\">■ カウンタ $b_title ■</FONT></TH></TR>
		<TR><TD CLASS=\"head\">カウンターコード</TH>
		<TD CLASS=\"form\">$hbuf_ccode</TD></TR>
		<TR><TD CLASS=\"head\">延べアクセス数</TH>
		<TD CLASS=\"form\">
			現在＝<INPUT TYPE=\"text\" NAME=\"ca\" SIZE=\"8\" VALUE=\"$b_ca\">、
			昨日まで＝<INPUT TYPE=\"text\" NAME=\"cu\" SIZE=\"8\" VALUE=\"$b_cu\">、
			昨日＝<INPUT TYPE=\"text\" NAME=\"cy\" SIZE=\"5\" VALUE=\"$b_cy\">
		</TD>
		</TR>
		<TR><TD CLASS=\"head\">ホストアクセス数</TH>
		<TD CLASS=\"form\">
			現在＝<INPUT TYPE=\"text\" NAME=\"cah\" SIZE=\"8\" VALUE=\"$b_cah\">、
			昨日まで＝<INPUT TYPE=\"text\" NAME=\"cuh\" SIZE=\"8\" VALUE=\"$b_cuh\">、
			昨日＝<INPUT TYPE=\"text\" NAME=\"cyh\" SIZE=\"5\" VALUE=\"$b_cyh\">
		</TD>
		</TR>
		<TR><TH COLSPAN=\"2\" CLASS=\"key\">
		$hbuf_del
		<INPUT TYPE=\"submit\" NAME=\"exec\" VALUE=\"作業実行\">
		</FONT></TH></TR>
		<TR><TD CLASS=\"comm\" COLSPAN=\"2\">
		※ 延べアクセス数 … ページが開かれた回数（＝カウンタの数字画像が表\示された回数）<BR>
		※ ホストアクセス数 … 同じ日の同一ホストからのアクセスを一度しかカウントしない場合の回数<BR>
		※ 「今日」の数値は「現在－昨日まで」で算出しています。<BR>
		※ ここでの修正は集計済みの過去ログには一切影響を与えません。現在の格納値を変えるだけです。<BR>
		</TD></TR>
		
		</TABLE>
		</DIV>
		</FORM>
		<BR><BR>
	";
	
}



########## カウンタ一覧
sub html_table{
	local($htmlbuf, $b_ccode, );
	
	$htmlbuf = "
	<DIV ALIGN=\"center\">
	<TABLE WIDTH=\"80%\" BORDER=\"1\" CELLPADDING=\"1\" CELLSPACING=\"0\">
	<CAPTION>
	<B>登録情報一覧</B><BR>
	</CAPTION>
	<TR BGCOLOR=\"330000\">
	<TH CLASS=\"key\">code</TH>
	<TH CLASS=\"key\">累計</TH>
	<TH CLASS=\"key\">累計H</TH>
	<TH CLASS=\"key\">今日</TH>
	<TH CLASS=\"key\">今日H</TH>
	<TH CLASS=\"key\">昨日</TH>
	<TH CLASS=\"key\">昨日H</TH>
	<TH CLASS=\"key\">テスト</TH>
	</TR>
	";
	
	$i = 0;
	$bgs[0] = "#FFCCCC";
	$bgs[1] = "#FFFFFF";
	
	foreach (@g_codesort){
		($b_ccode, $b_ca, $b_cah) = split("\t", $CTDY{$_});
		($b_ccode, $b_cy, $b_cyh, $b_cu, $b_cuh) = split("\t", $CYST{$_});
		
		$htmlbuf .= "
		<TR BGCOLOR=\"$bgs[$i%2]\">
		<TH>
		<SPAN CLASS=\"emp\">$b_ccode</SPAN></TH>
		<TD>$b_ca<A HREF=\"./tc.cgi?$b_ccode&a\">[C]</A></TD>
		<TD>$b_cah<A HREF=\"./tc.cgi?$b_ccode&ah\">[C]</A></TD>
		<TD>$CCT{$_}<A HREF=\"./tc.cgi?$b_ccode&t\">[C]</A></TD>
		<TD>$CCTH{$_}<A HREF=\"./tc.cgi?$b_ccode&th\">[C]</A></TD>
		<TD>$b_cy<A HREF=\"./tc.cgi?$b_ccode&y\">[C]</A></TD>
		<TD>$b_cyh<A HREF=\"./tc.cgi?$b_ccode&yh\">[C]</A></TD>
		<TD>
		[<A HREF=\"./tc.cgi?$b_ccode&a&1\">Up</A>]
		</TD>
		</TR>
		";
		
		$i++;
	}
	
	$htmlbuf .= "
		<TR><TD CLASS=\"comm\" COLSPAN=\"8\">
		※ \"H\"はホストアクセス数の統計（詳しくは上記）<BR>
		※ \"[C]\"をクリックするとカウンタ画像が表\示されます。タグの確認などにお使い下さい。<BR>
		※ \"Up\"をクリックするとカウント数が増加します。動作確認にお使い下さい。<BR>
		※ スイッチの仕様 → コード&種類&増加&画像&桁数<BR>
		</TD></TR>
	";
	$htmlbuf .= "</TABLE></DIV>";
}



########## カウンタログ
sub html_log{
	local($htmlbuf, $hbuf_header, $hbuf_comment, $hbuf_day, $hbuf_month, $hbuf_all);
	local($b_ccode, $b_ca, $b_cah, $b_cd, $b_cdh, $b_cu, $b_cuh, $b_pmon, $b_date);
	local(@b_dayhsts, %IH, %DH, %MH, %AH);
	
	### ログファイルを開く
	&openfile($hstfile, *hsts);
	### 逆順にしつつ無視する日数分を削除
	foreach(@hsts)
	{
		($b_date, @b_dayhsts) = split("\t");
		foreach $bh(@b_dayhsts)
		{
			($b_id) = split("/", $bh);
			(++$IH{$b_id} > $AVG_IGNORE_DAYS_COUNT) || next;
			$b_date .= "\t$bh";
		}
		unshift(@bhsts, $b_date);
	}
	@hsts = @bhsts;
	
	
	### 集計期間
	$b_begin = (split("\t", $hsts[$#hsts]))[0];
	$b_end   = (split("\t", $hsts[0]))[0];
	$b_begin =~ s/(\d{2})(\d{2})(\d{2})(\d{2})/$2\/$3\/$4/;
	$b_end   =~ s/(\d{2})(\d{2})(\d{2})(\d{2})/$2\/$3\/$4/;
	
	
	### ヘッダ行
	$hbuf_header .= "<TR><TH CLASS=\"key\">Code = </TH>";
	foreach(@g_codesort){
		$hbuf_header .= "<TH CLASS=\"key\">$_</TH>";
	}
	$hbuf_header .= "</TR>\n";
	### コード数+1（colspan用）
	$b_tcols = @g_codesort + 1;
	
	
	### コメント
	$hbuf_comment = "
		<DIV CLASS=\"attention\">
		他のログファイルを見る → <A HREF=\"./$bakfile\">ホストログ</A> ／ <A HREF=\"./$logfile\">動作ログ</A><P>
		※ 表\示の見方：「<SPAN CLASS=\"d\">延べアクセス数</SPAN>／<SPAN CLASS=\"dh\">ホストアクセス数</SPAN>」、(xxx)は累計、[xxx]は日数<BR>
		※ 延べアクセス数 … ページが開かれた回数（＝カウンタの数字画像が表\示された回数）<BR>
		※ ホストアクセス数 … 同じ日の同一ホストからのアクセスを一度しかカウントしない場合の回数
		</DIV><P>
		";
	
	### 日単位表示ヘッダ
	$hbuf_day .= "
		<DIV ALIGN=\"left\">
		<TABLE BORDER=\"0\" CELLPADDING=\"2\" CELLSPACING=\"1\" BGCOLOR=\"#330000\">
		<TR><TD COLSPAN=\"$b_tcols\" CLASS=\"comm\"><SPAN CLASS=\"emp\">■ 日別統計</SPAN></TD></TR>
	";
	$hbuf_day .= $hbuf_header;
	
	### 月単位表示用ヘッダ
	$hbuf_month = "
		<DIV ALIGN=\"left\">
		<TABLE BORDER=\"0\" CELLPADDING=\"2\" CELLSPACING=\"1\" BGCOLOR=\"#330000\">
		<TR><TD COLSPAN=\"$b_tcols\" CLASS=\"comm\"><SPAN CLASS=\"emp\">■ 月別統計</SPAN></TD></TR>
		";
	$hbuf_month .= $hbuf_header;
	
	### 総計表示用ヘッダ
	$hbuf_all = "
		<DIV ALIGN=\"left\">
		<TABLE BORDER=\"0\" CELLPADDING=\"2\" CELLSPACING=\"1\" BGCOLOR=\"#330000\">
		<TR><TD COLSPAN=\"$b_tcols\" CLASS=\"comm\"><SPAN CLASS=\"emp\">■ 総合統計</SPAN>
		<SPAN CLASS=\"d\">（$b_begin～$b_end）</SPAN></TD></TR>
		";
	$hbuf_all .= $hbuf_header;
	
	### 曜日単位表示用ヘッダ
	$hbuf_week = "
		<DIV ALIGN=\"left\">
		<TABLE BORDER=\"0\" CELLPADDING=\"2\" CELLSPACING=\"1\" BGCOLOR=\"#330000\">
		<TR><TD COLSPAN=\"$b_tcols\" CLASS=\"comm\"><SPAN CLASS=\"emp\">■ 曜日別統計</SPAN></TD></TR>
		";
	$hbuf_week .= $hbuf_header;
	
	### 表示：今日
	$hbuf_day .=  "<TR><TD CLASS=\"ws\">（今日）</TD>";
	foreach(@g_codesort)
	{
		($b_ccode, $b_ca, $b_cah) = split("\t", $CTDY{$_});
		$hbuf_day .= "
			<TD CLASS=\"ws\">
			<SPAN CLASS=\"d\">$CCT{$_}</SPAN>/<SPAN CLASS=\"dh\">$CCTH{$_}</SPAN>
			(<SPAN CLASS=\"u\">$b_ca</SPAN>/<SPAN CLASS=\"uh\">$b_cah</SPAN>)
			</TD>
		";
	}
	$hbuf_day .= "</TR>\n";
	
	# 月代わり感知用
	$b_pmon = substr($hsts[0], 0, 6);
	# 最近×日間カウント用
	$b_rday = 0;
	# ダミー行
	push(@hsts, "00000000");
	
	### 表示：昨日以前
	foreach(@hsts)
	{
		# 日付の分離
		($b_date, @b_dayhsts) = split("\t");
		$b_sdate = $b_date;
		$b_sdate =~ s/(\d{2})(\d{2})(\d{2})(\d{2})/$2\/$3\/$4/;
		# 曜日の取得
		$b_wday = &date2wday($2, $3, $4);
		
		# 月が変わったらヘッダ再表示
		if($b_pmon ne substr($b_date, 0, 6))
		{
			($b_pmon) || last;
			substr($b_pmon, 4, 0, "/");
			
			$hbuf_month .= "<TR><TD CLASS=\"ws\">$b_pmon 総合</TD>";
			
			# 月総合
			foreach(@g_codesort)
			{
				$b_cd = $MH{"T/$_"};
				$b_cdh = $MH{"TH/$_"};
				$b_cdd = $MH{"D/$_"} || "0";
				$hbuf_month .= "
					<TD CLASS=\"ws\">
					<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
					<SPAN CLASS=\"dd\">[$b_cdd]</SPAN>
					</TD>
					";
			}
			$hbuf_month .= "</TR>\n";
			
			# 月平均
			$hbuf_month .= "<TR><TD CLASS=\"w3\">$b_pmon 平均</TD>";
			foreach(@g_codesort)
			{
				($MH{"D/$_"}) || ($MH{"D/$_"} = 1);
				$b_cd = sprintf("%.2f", $MH{"T/$_"} / $MH{"D/$_"});
				$b_cdh = sprintf("%.2f", $MH{"TH/$_"} / $MH{"D/$_"});
				$hbuf_month .= "
					<TD CLASS=\"w3\">
					<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
					</TD>
					";
			}
			$hbuf_month .= "</TR>\n";
			
			# 次のヘッダ
			$hbuf_day .= $hbuf_header;
			# 後始末
			$b_pmon = substr($b_date, 0, 6);
			undef(%MH);
		}
		
		### 日付が終末ダミーに達していたら終了
		($b_date eq "00000000") && last;
		
		# 日数のカウント
		undef(%DH);
		foreach(@b_dayhsts){
			($b_ccode) = split("/");
			# 整列表示するので一旦ハッシュに入れる
			$DH{$b_ccode} = $_;
			# 日数のカウント
			$AH{"D/$b_ccode"}++;
			$MH{"D/$b_ccode"}++;
			$WH{"D/$b_wday/$b_ccode"}++;
			if($b_rday < $RECENT_DAYS_COUNT){
				$RH{"D/$b_ccode"}++;
			}
		}
		
		# 日付の表示
		$hbuf_day .= "<TR><TD CLASS=\"w$b_wday\">$b_sdate</TD>";
		
		foreach(@g_codesort){
			($b_ccode, $b_cd, $b_cdh, $b_cu, $b_cuh) = split("/", $DH{$_});
			$MH{"T/$_"} += $b_cd;
			$MH{"TH/$_"} += $b_cdh;
			$AH{"T/$_"} += $b_cd;
			$AH{"TH/$_"} += $b_cdh;
			$WH{"T/$b_wday/$_"} += $b_cd;
			$WH{"TH/$b_wday/$_"} += $b_cdh;
			if($b_rday < $RECENT_DAYS_COUNT){
				$RH{"T/$_"} += $b_cd;
				$RH{"TH/$_"} += $b_cdh;
			}
			if($b_cd){
				$hbuf_day .= "
					<TD CLASS=\"w$b_wday\">
					<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
					(<SPAN CLASS=\"u\">$b_cu</SPAN>/<SPAN CLASS=\"uh\">$b_cuh</SPAN>)
					</TD>
					";
			}
			else{
				$hbuf_day .= "<TD CLASS=\"w$b_wday\"><SPAN CLASS=\"dd\">n/a</SPAN></TD>";
			}
		}
		$hbuf_day .= "</TR>\n";
		# 最近の日数
		($b_rday < $RECENT_DAYS_COUNT) && ($b_rday++);
	}
	$hbuf_day .= "</TABLE></DIV>";
	
	### 月単位：閉じる
	$hbuf_month .= "</TABLE></DIV><P>";
	
	### 総合：総計
	$hbuf_all .= "<TR><TD CLASS=\"ws\">全期間</TD>";
	foreach(@g_codesort)
	{
		$b_cd = $AH{"T/$_"};
		$b_cdh = $AH{"TH/$_"};
		$b_cdd = $AH{"D/$_"} || "0";
		$hbuf_all .= "
			<TD CLASS=\"ws\">
			<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
			<SPAN CLASS=\"dd\">[$b_cdd]</SPAN>
			</TD>
			";
	}
	$hbuf_all .= "</TR>";
	
	### 総合：平均
	$hbuf_all .= "<TR><TD CLASS=\"w3\">全期間・平均</TD>";
	foreach(@g_codesort)
	{
		($AH{"D/$_"}) || ($AH{"D/$_"} = 1);
		$b_cd = sprintf("%.2f", $AH{"T/$_"} / $AH{"D/$_"});
		$b_cdh = sprintf("%.2f", $AH{"TH/$_"} / $AH{"D/$_"});
		$hbuf_all .= "
			<TD CLASS=\"w3\">
			<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
			</TD>
			";
	}
	$hbuf_all .= "</TR>";
	
	### 最近×日間：総計
	$hbuf_all .= "<TR><TD CLASS=\"ws\">最近$b_rday日間・総計</TD>";
	foreach(@g_codesort)
	{
		$b_cd = $RH{"T/$_"};
		$b_cdh = $RH{"TH/$_"};
		$hbuf_all .= "
			<TD CLASS=\"ws\">
			<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
			</TD>
			";
	}
	$hbuf_all .= "</TR>";
	
	### 最近×日間：平均
	$hbuf_all .= "<TR><TD CLASS=\"w3\">最近$b_rday日間・平均</TD>";
	foreach(@g_codesort)
	{
		($RH{"D/$_"}) || ($RH{"D/$_"} = 1);
		$b_cd = sprintf("%.2f", $RH{"T/$_"} / $RH{"D/$_"});
		$b_cdh = sprintf("%.2f", $RH{"TH/$_"} / $RH{"D/$_"});
		$hbuf_all .= "
			<TD CLASS=\"w3\">
			<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
			</TD>
			";
	}
	$hbuf_all .= "</TR></TABLE></DIV><P>";
	
	### 曜日別
	$WK[0] = "日"; $WK[1] = "月"; $WK[2] = "火"; $WK[3] = "水"; 
	$WK[4] = "木"; $WK[5] = "金"; $WK[6] = "土"; 
	for($wd = 0; $wd<=6; $wd++)
	{
		$hbuf_week .= "<TR><TD CLASS=\"w$wd\">$WK[$wd]曜</TD>";
		foreach(@g_codesort)
		{
			$b_cd = $WH{"T/$wd/$_"};
			$b_cdh = $WH{"TH/$wd/$_"};
			$b_cdd = $WH{"D/$wd/$_"} || "0";
			$hbuf_week .= "
				<TD CLASS=\"ws\">
				<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
				<SPAN CLASS=\"dd\">[$b_cdd]</SPAN>
				</TD>
				";
		}
		$hbuf_week .= "</TR><TR><TD CLASS=\"w$wd\">$WK[$wd]曜・平均</TD>";
		foreach(@g_codesort)
		{
			($WH{"D/$wd/$_"}) || ($WH{"D/$wd/$_"} = 1);
			$b_cd = sprintf("%.2f", $WH{"T/$wd/$_"} / $WH{"D/$wd/$_"});
			$b_cdh = sprintf("%.2f", $WH{"TH/$wd/$_"} / $WH{"D/$wd/$_"});
			$hbuf_week .= "
				<TD CLASS=\"w3\">
				<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
				</TD>
				";
		}
	}
	$hbuf_week .= "</TR></TABLE></DIV><P>";
	
	
	### 表示順の決定
	$htmlbuf = $hbuf_comment . $hbuf_all . $hbuf_month . $hbuf_week . $hbuf_day;
	
	return $htmlbuf;
}



########## コピーライト
sub copyright{
	"
<TABLE ALIGN=\"right\" BORDER=\"0\" CELLPADDING=\"1\" CELLSPACING=\"1\" BGCOLOR=\"#990000\">
<TR><TH BGCOLOR=\"#FFFFCC\">
<A HREF=\"http://www.mytools.net/\" TARGET=\"_top\">
<FONT SIZE=\"2\" COLOR=\"#660000\">Powered by T-Count Ver.$verno</A>
</FONT></TH></TR></TABLE>
	";
}



########## ファイルを開いて、中身を配列に代入する
sub openfile{
	local ($filename, *bufs, $frag) = @_;
	
	(-f $filename) || ($frag) || &error(981, "ファイルが存在しません：$filename");
	open(FILE, "$filename") || ($frag) || &error(982, "ファイルを読み込みモードで開くことができません：$filename");
	@bufs = <FILE>;
	close(FILE);
	
	(@bufs) ? return(1) : return(0);
}



########## ファイルを更新する
sub updatefile{
	local ($filename, *buf, $frag) = @_;
	
	(-f $filename) || &error(383, "ファイルが存在しません：$filename");
	# フラグあり→追加、なし→更新
	if($frag){
		open(FILE, ">>$filename") || &error(384, "ファイルを追記モードで開くことができません：$filename");
	}
	else{
		open(FILE, ">$filename") || &error(385, "ファイルを書き込みモードで開くことができません：$filename");
	}
	print FILE @buf;
	close(FILE);
}



##### 日付→曜日変換
sub date2wday
{
	local($year, $mon, $day) = @_;
	if($mon < 3){ $year--; $mon += 12; }
	return ($year + int($year/4) - int($year/100) + int($year/400) + int((13 * $mon + 8) / 5) + $day) % 7;
}



##### ファイルロック
sub lock
{
	local($try) = 5;
	while(!(mkdir($lockfile, 0700))){
		if(--$try > 0){
			&error(100, "ロック中です");
		}
		sleep(3);
	}
}



##### ロック解除
sub unlock
{
	rmdir($lockfile);
}



##### エラー表示
sub error
{
	local($code, $errmsg) = @_;
	local(@sts) = lstat($lockfile);
	local($tn) = time();
	
	print "
<HTML>
<HEAD><TITLE>T-Count 5 - Error!!</TITLE></HEAD>
<BODY BGCOLOR=\"#FFFFFF\">
<FONT SIZE=\"3\">
<H3>エラー発生</H3>
ERR-$code: 
<FONT COLOR=\"#FF0000\">$errmsg</FONT><P>
<HR NOSHADE SIZE=\"1\">
<FONT SIZE=\"2\">
<B>管理者：<A HREF=\"mailto:$admin_email\">$admin_email</A></B><BR>
※ ご一報の際にはサイトのＵＲＬと症状をお書き添え下さいますようお願いします。
</FONT>
";
	
	($code == 100) || &unlock; # ID が 100 以外の場合はロック解除
	($tn - $sts[9] < 15) || &unlock; # 約15秒以上ロックが続いてたら自動解除
	exit;
}
