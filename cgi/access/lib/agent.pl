#=====================================================================
# access cgi UserAgent解析ライブラリ agent.pl (2002/05/23)
#=====================================================================
# UserAgent 解析処理

sub user_agent {

	$agent = $user_agent;

	$agent =~ s/M\$IE/MSIE/ig;
	$agent =~ s/Window\$/Windows/ig;
	$agent =~ s/Windows ME/Win 9x 4.90/ig;
	$agent =~ s/Windows 2000|Windows2000/Windows NT 5.0/ig;
	$agent =~ s/Windows XP/Windows NT 5.1/ig;

	$os = $agent;

#---------------------------------------------------------------------
# agent 解析

# Google

	if ($agent =~ /Google CHTML Proxy/i) { $agent = 'Google i-mode'; }

# 携帯電話

	elsif ($agent =~ /DoCoMo/i) { $agent = 'i-mode'; }
	elsif ($agent =~ /UP.Browser/i) { $agent = 'EZweb'; }

# アンテナ

	elsif ($agent =~ /NATSU-MICAN/i) { $agent = 'なつみかん'; }
	elsif ($agent =~ /MICAN/i) { $agent = 'MICAN'; }
	elsif ($agent =~ /Antenna/i) { $agent = '朝日奈アンテナ'; }
	elsif ($agent =~ /WDB/i) { $agent = 'WDB'; }
	elsif ($agent =~ /TAMATEBAKO/i) { $agent = 'たまてばこ'; }

# 巡回ツール

	elsif ($agent =~ /WWWC/i) { $agent = 'WWWC'; }
	elsif ($agent =~ /WWWD/i) { $agent = 'WWWD'; }
	elsif ($agent =~ /INCM/i) { $agent = 'INCM'; }
	elsif ($agent =~ /mamimi/i) { $agent = 'mamimi'; }

# Web filter

	elsif ($agent =~ /SpaceBison|ShonenKnife|Proxomitron/i) { $agent = 'Proxomitron'; }
	elsif ($agent =~ /Blocked by Norton/i) { $agent = 'Blocked by Norton'; }

#---------------------

	elsif ($ua_view) {

		if ($agent =~ /PS2; .*?\) NetFront\/(.+?)( |;|\)|$)/i) { $agent = "NetFront $1 (PS2)"; }
		elsif ($agent =~ /DreamPassport\/(.+?)( |;|\)|$)/i) { $agent = "DreamPassport $1"; }
		elsif ($agent =~ /sharp pda browser\/(.+?)(\[| |;|\)|$)/i) { $agent = "sharp pda browser $1"; }
		elsif ($agent =~ /AVE-Front\/(.+?)( |;|\)|$)/i) { $agent = "AVE-Front $1"; }
		elsif ($agent =~ /NetFront\/(.+?)( |;|\)|$)/i) { $agent = "NetFront $1"; }
		elsif ($agent =~ /^amaya\/(.+?)( |;|\)|$)/i) { $agent = "Amaya $1"; }
		elsif ($agent =~ /^Lynx\/(.+?) /i) { $agent = "Lynx $1"; }
		elsif ($agent =~ /^w3m\/(.+?)$/i) { $agent = "w3m $1"; }
		elsif ($agent =~ /iCab .\/(.+?) /i) { $agent = "iCab $1"; }
		elsif ($agent =~ /NetCaptor (.+?)( |;|\)|$)/i) { $agent = "NetCaptor $1"; }
		elsif ($agent =~ /OmniWeb\/(.+?)( |;|\)|$)/i) { $agent = "OmniWeb $1"; }
		elsif ($agent =~ /Konqueror\/(.+?);/i) { $agent = "Konqueror $1"; }
		elsif ($agent =~ /Opera(\/| )(.+?) /i) { $agent = "Opera $2"; }
		elsif ($os =~ /Mac/i && $agent =~ /MSIE (.+?);/i) { $agent = "MacIE $1"; }
		elsif ($agent =~ /MSIE (.+?);/i) { $agent = "WinIE $1"; }
		elsif ($agent =~ /Netscape(\d+\/|\/)(.+?)$/i) { $agent = "Netscape $2"; }
		elsif ($agent =~ /Mozilla\/4(.+?) /i) { $agent = "Netscape 4$1"; }
		elsif ($agent =~ /Mozilla\/5/i && $agent =~ /rv:(.+?)\) Gecko\//i) { $agent = "Mozilla $1"; }
		elsif ($agent =~ /Gecko\/(\d+)/i) { $agent = "Gecko $1"; }
		else { if ($ua_others) { $agent = '[others]'; } }

	} else {

# PlayStation 2 or DreamCast
# Mozilla/4.0 (PS2; PlayStation BB Navigator 1.0) NetFront/3.0

		if ($agent =~ /PS2; .*?\) NetFront/i) { $agent = 'NetFront (PS2)'; }
		elsif ($agent =~ /DreamPassport/i) { $agent = 'DreamPassport'; }

# PDA

		elsif ($agent =~ /sharp pda browser/i) { $agent = 'sharp pda browser'; }
		elsif ($agent =~ /AVE-Front/i) { $agent = 'AVE-Front'; }
		elsif ($agent =~ /NetFront/i) { $agent = 'NetFront'; }

# UserAgent

		elsif ($agent =~ /^amaya/i) { $agent = 'Amaya'; }
		elsif ($agent =~ /^Lynx/i) { $agent = 'Lynx'; }
		elsif ($agent =~ /^w3m/i) { $agent = 'w3m'; }

		elsif ($agent =~ /iCab/i) { $agent = 'iCab'; }
		elsif ($agent =~ /NetCaptor/i) { $agent = 'NetCaptor'; }
		elsif ($agent =~ /OmniWeb/i) { $agent = 'OmniWeb'; }
		elsif ($agent =~ /Konqueror\/(.+?);/i) { $agent = "Konqueror"; }

		elsif ($agent =~ /Opera(\/| )6/i) { $agent = 'Opera 6'; }
		elsif ($agent =~ /Opera(\/| )5/i) { $agent = 'Opera 5'; }

		elsif ($os =~ /Mac/i && $agent =~ /MSIE 5\.5/i) { $agent = 'MacIE 5.5'; }
		elsif ($os =~ /Mac/i && $agent =~ /MSIE 5\.1/i) { $agent = 'MacIE 5.1'; }
		elsif ($os =~ /Mac/i && $agent =~ /MSIE 5\.0/i) { $agent = 'MacIE 5'; }
		elsif ($os =~ /Mac/i && $agent =~ /MSIE 4\.5/i) { $agent = 'MacIE 4.5'; }
		elsif ($os =~ /Mac/i && $agent =~ /MSIE 4\.0/i) { $agent = 'MacIE 4'; }

		elsif ($agent =~ /MSIE 7\.0/i) { $agent = 'WinIE 7.0'; }
		elsif ($agent =~ /MSIE 6\.0/i) { $agent = 'WinIE 6.0'; }
		elsif ($agent =~ /MSIE 5\.5/i) { $agent = 'WinIE 5.5'; }
		elsif ($agent =~ /MSIE 5\.0/i) { $agent = 'WinIE 5'; }
		elsif ($agent =~ /MSIE 4/i) { $agent = 'WinIE 4'; }
		elsif ($agent =~ /MSIE 3/i) { $agent = 'WinIE 3'; }

		elsif ($agent =~ /Netscape\/7/i) { $agent = 'Netscape 7'; }
		elsif ($agent =~ /Netscape6/i) { $agent = 'Netscape 6'; }
		elsif ($agent =~ /Mozilla\/4/i) { $agent = 'Netscape 4'; }

		elsif ($agent =~ /Mozilla\/5/i && $agent =~ /rv:(.+?)\) Gecko\//i) { $agent = "Mozilla"; }
		elsif ($agent =~ /Gecko/i) { $agent = 'Gecko'; }

# Others

		else { if ($ua_others) { $agent = '[others]'; } }

	}

#---------------------------------------------------------------------
# OS 解析

# Google

	if ($os =~ /Google CHTML Proxy/i) { $os = 'Google i-mode'; }

# 携帯電話

	elsif ($os =~ /DoCoMo/i) { $os = 'i-mode'; }
	elsif ($os =~ /UP.Browser/i) { $os = 'EZweb'; }

# アンテナ

	elsif ($os =~ /NATSU-MICAN/i) { $os = 'なつみかん'; }
	elsif ($os =~ /MICAN/i) { $os = 'MICAN'; }
	elsif ($os =~ /Antenna/i) { $os = '朝日奈アンテナ'; }
	elsif ($os =~ /WDB/i) { $os = 'WDB'; }
	elsif ($os =~ /TAMATEBAKO/i) { $os = 'たまてばこ'; }

# Mac or Win or Unix

	elsif ($os =~ /Mac/i) { $os = 'Mac'; }

	elsif ($os =~ /Win 9x 4\.90/i) { $os = 'WinMe'; }
	elsif ($os =~ /Windows 98|Win98/i) { $os = 'Win98'; }
	elsif ($os =~ /Windows 95|Win95/i) { $os = 'Win95'; }
	elsif ($os =~ /Windows CE|WinCE/i) { $os = 'WinCE'; }

	elsif ($os =~ /Windows NT 5\.1/i) { $os = 'WinXP'; }
	elsif ($os =~ /Windows NT 5\.0/i) { $os = 'Win2000'; }
	elsif ($os =~ /Windows NT|WinNT/i) { $os = 'WinNT'; }

	elsif ($os =~ /Linux/i) { $os = 'Linux'; }
	elsif ($os =~ /FreeBSD/i) { $os = 'FreeBSD'; }
	elsif ($os =~ /\(X1|Sun/i) { $os = 'UNIX'; }

# 巡回ツール

	elsif ($os =~ /WWWC/i) { $os = 'WWWC'; }
	elsif ($os =~ /WWWD/i) { $os = 'WWWD'; }
	elsif ($os =~ /INCM/i) { $os = 'INCM'; }
	elsif ($os =~ /mamimi/i) { $os = 'mamimi'; }

# Web filter

	elsif ($os =~ /SpaceBison|ShonenKnife|Proxomitron/i) { $os = 'Proxomitron'; }
	elsif ($os =~ /Blocked by Norton/i) { $os = 'Blocked by Norton'; }

# Others

	else { if ($os_others) { $os = '[others]'; } }

#---------------------------------------------------------------------
# OS + agent

	if ($agent eq $os) { $osa = $agent; }
	else { $osa = "$agent ($os)"; }

}

#=====================================================================

# UserAgent を MSIE より継承するもの
# BugBrowser,Donut,Donut R,fub,MDIWeb,MoonBrowser,
# NeoPlanet,Net Sailer,TaBrowser,Web SurfACE,

# UserAgent を Gecko より継承するもの（一部未検証）
# K-Meleon,Beonex,Bezilla,Warpzilla,

# 一部、Web Designing 02 P.111 を参考資料とした。

#=====================================================================

1; # return
