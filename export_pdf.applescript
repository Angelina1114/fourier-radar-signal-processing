-- Usage: osascript export_pdf.applescript /abs/path/deck.pptx /abs/path/out.pdf
on run argv
	set inFile to POSIX file (item 1 of argv)
	set outFile to POSIX file (item 2 of argv)
	with timeout of 900 seconds
		tell application id "com.apple.Keynote"
			close every document saving no
			set theDoc to open inFile
			export theDoc to outFile as PDF with properties {PDF image quality:Best, skipped slides:false}
			close theDoc saving no
		end tell
	end timeout
end run
