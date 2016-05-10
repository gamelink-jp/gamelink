#=====================================================================
# access cgi 検索サービス解析ライブラリ search.pl (2002/04/15)
#=====================================================================
# 検索キーワード情報解析処理

sub search_service {

	$refq = $refs = ''; 

	if ($ref =~ /google\..*?(\?|\&)(q|query|as_q)=(.*?)(\&|$)/i) { $refq = $3; $refs = 'Google'; }	# Google
	elsif ($ref =~ /yahoo\..*?(\?|\&)p=(.*?)(\&|$)/i) { $refq = $2; $refs = 'Yahoo'; }				# Yahoo!
	elsif ($ref =~ /goo\..*?(\?|\&)MT=(.*?)(\&|$)/i) { $refq = $2; $refs = 'goo'; }					# goo
	elsif ($ref =~ /infoseek\..*?(\?|\&)qt=(.*?)(\&|$)/i) { $refq = $2; $refs = 'infoseek'; }		# infoseek
	elsif ($ref =~ /excite\..*?(\?|\&)(s|search)=(.*?)(\&|$)/i) { $refq = $3; $refs = 'Excite'; }	# Excite
	elsif ($ref =~ /lycos\..*?(\?|\&)(q|query)=(.*?)(\&|$)/i) { $refq = $3; $refs = 'LYCOS'; }		# LYCOS
	elsif ($ref =~ /fresheye\..*?(\?|\&)kw=(.*?)(\&|$)/i) { $refq = $2; $refs = 'FreshEye'; }		# FreshEye
	elsif ($ref =~ /alltheweb\..*?(\?|\&)query=(.*?)(\&|$)/i) { $refq = $2; $refs = 'AllTheWeb'; }	# All The Web
	elsif ($ref =~ /altavista\..*?(\?|\&)q=(.*?)(\&|$)/i) { $refq = $2; $refs = 'AltaVista'; }		# AltaVista
	elsif ($ref =~ /naver\..*?(\?|\&)query=(.*?)(\&|$)/i) { $refq = $2; $refs = 'NAVER'; }			# NAVER
	elsif ($ref =~ /odin\..*?(\?|\&)key=(.*?)(\&|$)/i) { $refq = $2; $refs = 'ODIN'; }				# ODIN
	elsif ($ref =~ /isize\..*?(\?|\&)QueryString=(.*?)(\&|$)/i) { $refq = $2; $refs = 'ISIZE'; }	# ISIZE
	elsif ($ref =~ /search\.msn\..*?(\?|\&)(q|MT)=(.*?)(\&|$)/i) { $refq = $3; $refs = 'MSN'; }		# MSN Search
	elsif ($ref =~ /search\.netjoy\..*?(\?|\&)key=(.*?)(\&|$)/i) { $refq = $2; $refs = 'JOY'; }		# JOY
	elsif ($ref =~ /kensaku\..*?search\.cgi.*?(\?|\&)key=(.*?)(\&|$)/i) { $refq = $2; $refs = 'kensaku'; }	# kensaku.jp
	elsif ($ref =~ /nifty\..*?search\.cgi.*?(\?|\&)Text=(.*?)(\&|$)/i) { $refq = $2; $refs = '@search'; }	# @search
	elsif ($ref =~ /search\.biglobe\..*?(\?|\&)q=(.*?)(\&|$)/i) { $refq = $2; $refs = 'Attayo'; }			# Attayo!
	elsif ($ref =~ /search\.kingdom\.biglobe\..*?(\?|\&)key=(.*?)(\&|$)/i) { $refq = $2; $refs = 'Kingdom'; }	# BIGLOBE Personal Kingdom
	elsif ($ref =~ /para\.cab\.infoweb\..*?(\?|\&)Querystring=(.*?)(\&|$)/i) { $refq = $2; $refs = 'InfoNavi'; }	# InfoNavigator

}

#=====================================================================
# 検索サービス・リンク元情報置換設定

%searchsite = (

	'Google' , 'http://www.google.co.jp/' ,
	'Yahoo' , 'http://www.yahoo.co.jp/' ,
	'goo' , 'http://www.goo.ne.jp/' ,
	'infoseek' , 'http://www.infoseek.co.jp/' ,
	'Excite' , 'http://www.excite.co.jp/' ,
	'LYCOS' , 'http://www.lycos.co.jp/' ,
	'FreshEye' , 'http://www.fresheye.com/' ,
	'AllTheWeb' , 'http://www.alltheweb.com/' ,
	'AltaVista' , 'http://altavista.com/' ,
	'NAVER' , 'http://www.naver.co.jp/' ,
	'ODIN' , 'http://odin.ingrid.org/' ,
	'ISIZE' , 'http://www.isize.com/' ,
	'MSN' , 'http://search.msn.co.jp/' ,
	'JOY' , 'http://www.joyjoy.com/JOY.html' ,
	'kensaku' , 'http://kensaku.jp/' ,
	'@search' , 'http://www.nifty.com/search/' ,
	'Attayo' , 'http://search.biglobe.ne.jp/' ,
	'Kingdom' , 'http://search.biglobe.ne.jp/' ,
	'InfoNavi' , 'http://infonavi.infoweb.ne.jp/' ,

);

#=====================================================================
# 検索サービス・リンク元表示置換設定

%searchtitle = (

	'http://www.google.co.jp/' ,'[検索] Google' , 
	'http://www.yahoo.co.jp/' ,'[検索] Yahoo!' , 
	'http://www.goo.ne.jp/' ,'[検索] goo' , 
	'http://www.infoseek.co.jp/' ,'[検索] infoseek' , 
	'http://www.excite.co.jp/' ,'[検索] Excite' , 
	'http://www.lycos.co.jp/' ,'[検索] LYCOS' , 
	'http://www.fresheye.com/' ,'[検索] FreshEye' , 
	'http://www.alltheweb.com/' ,'[検索] All The Web' , 
	'http://altavista.com/' ,'[検索] AltaVista' , 
	'http://www.naver.co.jp/' ,'[検索] NAVER' , 
	'http://odin.ingrid.org/' ,'[検索] ODIN' , 
	'http://www.isize.com/' ,'[検索] ISIZE' , 
	'http://search.msn.co.jp/' ,'[検索] MSN Search' , 
	'http://www.joyjoy.com/JOY.html' ,'[検索] J.O.Y.' , 
	'http://kensaku.jp/' ,'[検索] kensaku.jp' , 
	'http://www.nifty.com/search/' ,'[検索] @search' , 
	'http://search.biglobe.ne.jp/' ,'[検索] Attayo!' , 
	'http://search.biglobe.ne.jp/' ,'[検索] BIGLOBE Personal Kingdom' , 
	'http://infonavi.infoweb.ne.jp/' ,'[検索] InfoNavigator' , 

);

#=====================================================================

1; # return
