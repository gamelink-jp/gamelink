#!/usr/bin/perl
#
######################################################################
###
###
###  CGIカウンター TcounT Ver.5.03
###     [1/2] 本体 (tc.cgi)
###                                 (c) 1996-2004 Takahiro Nishida
###                                 http://www.mytools.net/
###
###
######################################################################
#
### 変数設定部 （詳細は上記ページをご覧下さい） ######################

# データファイル格納位置
$basedir = ".";
# 時差修正
$time_fix = 0;

### 変数設定部 （ここまで）###########################################

# 最大桁数（カウンタ爆発防止）
$MAX_KETA_NUM = 20;


$lockfile = "$basedir/lockdir/tc.lock";
$allfile = "$basedir/tcdall.txt";
$ystfile = "$basedir/tcdyst.txt";
$hstfile = "$basedir/tcdhst.txt";
$logfile = "$basedir/tcdlog.txt";
$bakfile = "$basedir/tcdbak.txt";


require './gifcat.pl';

&main;



##### メイン
sub main
{
	&get_input;
	&lock;
	&open_datafile;
	if($m_incr)
	{
		&check_date;
		&increase_counter;
	}
	&unlock;
	&get_count;
	&show_counter;
}



##### 入力の取得
sub get_input
{
	$buffer = $ENV{'QUERY_STRING'};
	@m_prm = split("&", $buffer);
	
	$m_name = ($m_prm[0] =~ /^\w+$/) ? $m_prm[0] : ''   ;
	$m_type = ($m_prm[1] =~ /^\w+$/) ? $m_prm[1] : 'a'  ;
	$m_incr = ($m_prm[2] == 1)       ? 1         :  0   ;
	$m_gazo = ($m_prm[3] =~ /^\w+$/) ? $m_prm[3] : 'img';
	$m_keta = ($m_prm[4])            ? $m_prm[4] :  5   ;
	
	# カウンタ名が指定されていないとエラー
	($m_name) || &error(101, "カウンター名が指定されていません");
	# <gazo>ディレクトリがないとエラー
	(-d "$basedir/$m_gazo") || &error(102, "画像ディレクトリ($m_gazo)がありません");
	
	# ホスト
	$remote_host = $ENV{'REMOTE_HOST'} || &nslook($ENV{'REMOTE_ADDR'}) || $ENV{'REMOTE_ADDR'};
}



##### 各種データファイルを開く
sub open_datafile
{
	### 総合ファイル
	open(FILE, $allfile) || &error(111, "ファイル tcdall.txt が開けません");
	@tdys = <FILE>;
	close(FILE);
	
	### クラッシュリカバリ
	($tdys[0]) || &recover_counter;
	
	### 前回の記録日付
	$date_rec = $tdys[0] || "00000000\n";
	chop($date_rec);
	
	### 対象レコード検索
	$g_rno = -1;
	foreach(@tdys)
	{
		$g_rno++;
		(/^$m_name\t/) || next;
		($tmp, $g_a, $g_ah) = split("\t");
		last;
	}
	defined($g_a) || &error(112, "カウンタ名 $m_name は設定されていません");
}



##### 統計の取得
sub check_date
{
	# 増加フラグがある場合のみ判定を実行 → (030806)mainに移行
#	($m_incr) || return;
	
	# 日付が変わっているかチェック
	($tmp, $tmp, $tmp, $mday, $mon, $year) = localtime(time() + 60 * 60 * $time_fix);
	$mon++;
	$year += 1900;
	$date_now = sprintf("%04d%02d%02d", $year, $mon, $mday);
	
	# 日付が変わっていなかったら戻る
	($date_now > $date_rec) || return;
	
	##### 以下サマリ作成部
	&update_summery;
}



##### カウントアップ
sub increase_counter
{
	# 増加フラグかつ総合の場合のみ実行 → (030806)mainに移行
#	($m_incr && $m_type =~ /a/) || return;
	
	# 総合カウントアップ（とりあえず両方）
	$g_a++;
	$g_ah++;
	
	# ホスト重複チェック
	open(FILE, $bakfile) || &error(121, "ファイル tcdbak.txt が開けません");
	foreach(<FILE>)
	{
		(/\t$m_name\t$remote_host\t/) || next;
		# 重複してたら戻す
		$g_ah--;
		last;
	}
	close(FILE);
	
	# 新しい行の作成
	$tdys[$g_rno] = "$m_name\t$g_a\t$g_ah\t\n";
	
	# ファイルの更新
	open(FILE, ">$allfile") || &error(122, "ファイル tcdall.txt に書き込めません");
	print FILE @tdys;
	close(FILE);
	
	# ログの記録
	($sec, $min, $hour) = localtime(time() + 60 * 60 * $time_fix);
	$accesstime = sprintf("%02d:%02d:%02d", $hour, $min, $sec);
	open(FILE, ">>$bakfile") || &error(123, "ファイル tcdbak.txt が開けません");
	print FILE "$accesstime\t$m_name\t$remote_host\t\n";
	close(FILE);
}



##### 表示すべき値の取得
sub get_count
{
	### 総合
	if($m_type eq "a"){
		$g_shownum = $g_a;
	}
	### 総合ホスト
	elsif($m_type eq "ah"){
		$g_shownum = $g_ah;
	}
	else
	{
		### 昨日ファイルを開く
		open(FILE, $ystfile) || &error(131, "ファイル tcdyst.txt が開けません");
		foreach(<FILE>)
		{
			(/^$m_name\t/) || next;
			($tmp, $b_y, $b_yh, $b_ty, $b_tyh) = split("\t");
			last;
		}
		close(FILE);
		### 昨日
		if($m_type eq "y"){
			$g_shownum = $b_y;
		}
		### 昨日ホスト
		elsif($m_type eq "yh"){
			$g_shownum = $b_yh;
		}
		### 今日
		elsif($m_type eq "t"){
			$g_shownum = $g_a - $b_ty;
		}
		### 今日ホスト
		elsif($m_type eq "th"){
			$g_shownum = $g_ah - $b_tyh;
		}
		else{
			&error(132, "TYPE $m_type は存在しません");
		}
	}
}



##### カウンター画像の表示
sub show_counter
{
	@nums = split("", $g_shownum);
	(@nums > $MAX_KETA_NUM) && &error(141, "桁数が上限($MAX_KETA_NUM)を超えています。表示できません。");
	
	while(@nums < $m_keta){
		unshift(@nums, "0");
	}
	
	for(0..$#nums){
		$nums[$_] = "$basedir/$m_gazo/$nums[$_].gif";
	}
	
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);
	$| = 1;
	print &gifcat'gifcat(@nums);
}



##### 日が代わったときの処理
sub update_summery
{
	
	### 統計開始ログ
	&writelog("Date has changed. Create summery start.");
	
	### 日付更新
	$tdys[0] = "$date_now\n";
	
	### 昨日ファイルを開いてハッシュ化
	open(FILE, $ystfile) || &error(151, "ファイル tcdyst.txt が開けません");
	foreach(<FILE>)
	{
		($b_name, $b_y, $b_yh, $b_ty, $b_tyh) = split("\t");
		$HTIY{$b_name} = $b_ty;
		$HTIH{$b_name} = $b_tyh;
	}
	close(FILE);
	
	### 統計と新しい昨日ファイルの作成
	$b_newhst = "$date_rec\t";
	foreach(@tdys)
	{
		(/\t/) || next;
		($b_name, $b_a, $b_ah) = split("\t");
		$b_tdy  = $b_a  - $HTIY{$b_name};
		$b_tdyh = $b_ah - $HTIH{$b_name};
		### 統計
		$b_newhst .= "$b_name/$b_tdy/$b_tdyh/$b_a/$b_ah\t";
		### 昨日ファイル
		$b_newyst .= "$b_name\t$b_tdy\t$b_tdyh\t$b_a\t$b_ah\t\n";
	}
	$b_newhst .= "\n";
	
	### 統計の記録
	open(FILE, ">>$hstfile") || &error(152, "ファイル tcdhst.txt に書き込めません");
	print FILE $b_newhst;
	close(FILE);
	
	### 昨日ファイルの書き換え
	open(FILE, ">$ystfile") || &error(153, "ファイル tcdyst.txt に書き込めません");
	print FILE $b_newyst;
	close(FILE);
	
	### バックアップファイルのクリア
	open(FILE, ">$bakfile") || &error(154, "ファイル tcdbak.txt に書き込めません");
	close(FILE);
	
	### 動作ログファイルのクリア
	open(FILE, ">$logfile") || &error(155, "ファイル tcdlog.txt に書き込めません");
	close(FILE);
	
	### 統計開始ログ
	&writelog("Create summery finish.");
}



##### リカバリー
sub recover_counter
{
	### リカバリ開始
	&writelog("Datafile crash has detected. Start recovery.");
	
	### 昨日までの件数を取得
	open(FILE, $ystfile) || &error(161, "ファイル tcdyst.txt が開けません");
	foreach(<FILE>)
	{
		($b_name, $b_y, $b_yh, $b_ty, $b_tyh) = split("\t");
		$HA{$b_name} = $b_ty;
		$HAH{$b_name} = $b_tyh;
		push(@order, $b_name);
	}
	close(FILE);
	
	### バックアップを読みつつカウント復元
	open(FILE, $bakfile) || &error(162, "ファイル tcdbak.txt が開けません");
	foreach(<FILE>)
	{
		($tmp, $b_name, $b_host) = split("\t");
		$HA{$b_name}++;
		($HHOST{$b_host}) && next;
		$HAH{$b_name}++;
		$HHOST{$b_host} = 1;
	}
	close(FILE);
	
	##### 「前日」の取得
	($tmp, $tmp, $tmp, $mday, $mon, $year) = localtime(time() + 60 * 60 * $time_fix);
	$mon++;
	$year += 1900;
	$date_yst = sprintf("%04d%02d%02d", $year, $mon, $mday);
	
	### 今日データの再作成
	$i = 0;
	$tdys[0] = "$date_yst\n";
	foreach(@order){
		$tdys[++$i] = "$_\t$HA{$_}\t$HAH{$_}\t\n";
		&writelog("$_: Recovered to a=$HA{$_}, ah=$HAH{$_}");
	}
	
	### 今日ファイルの再作成
	open(FILE, ">$allfile") ||  &error(163, "ファイル tcdall.txt に書き込めません");
	print FILE @tdys;
	close(FILE);
	
	&writelog("Recovery has been finished.");
	
	&error(164, "カウンタのリカバー／初期化が完了しました。");
}



##### ログ記録
sub writelog
{
	local($msg) = @_;
	
	($sec, $min, $hour, $mday, $mon, $year) = localtime(time() + 60 * 60 * $time_fix);
	$mon++;
	$year += 1900;
	$logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);
	
	open(FILE, ">>$logfile") || &error(171, "ファイル tcdlog.txt に書き込めません");
	print FILE "$logtime $msg\n";
	close(FILE);
}



##### IPからHOST取得
sub nslook
{
	local($ip) = @_;
	$ip =~ /([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)/;
	return gethostbyaddr(pack('C4', $1, $2, $3, $4), 2);
}



##### ファイルロック
sub lock
{
	local($try) = 10;
	while(!(mkdir($lockfile, 0700))){
		if(--$try > 0){
			&writelog("$m_name: Locking.");
			&error(100, "ロック中です");
		}
		sleep(1);
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
	local($id, $errmsg) = @_;
	local(@sts) = lstat($lockfile);
	local($tn) = time();
	
	print "Content-type: text/plain\n\n";
	print "Error (Code:$id) - $errmsg";
	
	($id == 100) || &unlock; # ID が 100 以外の場合はロック解除
	($tn - $sts[9] < 15) || &unlock; # 約15秒以上ロックが続いてたら自動解除
	exit;
}
