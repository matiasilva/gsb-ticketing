# use `fd` for paralell execution
mkdir -p "pdfs"
fd -e svg GSB svgs/ -x inkscape {} --export-pdf=pdfs/{/.}.pdf