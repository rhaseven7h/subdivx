#!/usr/bin/env ruby
#
#   This file is part of SubDivX.
#
#   SubDivX is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License.
#
#   SubDivX is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with SubDivX, if not, see <http://www.gnu.org/licenses/>.
#
#   See the LICENSE file.
#

require 'rubygems'
require 'tmpdir'
require 'nokogiri'
require 'open-uri'
require 'gtk2'
require 'cgi'
require 'pp'

class SubDivXClient
  
  attr_accessor :results
  
  def initialize
    @results = []
  end
  
  def search(str_terms, page)
    str_url = "http://www.subdivx.com/index.php?buscar="+CGI.escape(str_terms)+"&accion=5&masdesc=1&subtitulos=1&realiza_b=1"
    if page > 1
      str_url += "&pg=#{page}"
    end
    doc = Nokogiri::HTML(open(str_url))
    titles = []
    links = []
    descriptions = []
    cds = []
    doc.css("a.titulo_menu_izq").each do |link|
      titles << link.content
      links << link[:href]
    end
    doc.css("div#buscador_detalle_sub").each do |desc|
      descriptions << desc.content
    end
    doc.css("div#buscador_detalle_sub_datos").each do |dato|
      cds << /Cds:<\/b> ([0-9]+)/.match(dato.to_s)[1].to_i
    end
    @results = []
    titles.each_index do |i|
      @results << { :title => titles[i], :link => links[i], :description => descriptions[i], :cds => cds[i].to_i }
    end
    @results
  end
  
  def fetch(int_num)
    doc = Nokogiri::HTML(open(@results[int_num][:link], "referer" => @results[int_num][:link]))
    desub = doc.css("input[type='hidden'][name='desub']")[0][:value]
    u = doc.css("input[type='hidden'][name='u']")[0][:value]
    fn = ""
    out_dir = File.join(Dir.tmpdir, "subdivx")
    out_file = ''
    open("http://www.subdivx.com/bajar.php?captcha_user=ME2&idcaptcha=1007&desub=#{desub}&u=#{u}", "referer" => @results[int_num][:link]) do |h|
      fn = h.meta["content-disposition"].split(';')[1].split('=')[1]
      out_file = File.join(out_dir, fn)
      FileUtils.mkdir_p(out_dir)
      File.open(out_file, "w") do |o|
        o.write(h.read)
      end
    end
    appdir = File.expand_path(File.dirname(__FILE__))
    return out_file
  end
  
end

class SubDivXGUI
  
  def initialize
    @subdivxclient = SubDivXClient.new
    @gtk = Gtk::Builder.new
    @gtk << open(__FILE__).readlines[210..-1].map{ |line| line[2..-1] }.join.unpack('u')[0]
    @gtk.connect_signals do |hn|
      case hn
        when "on_button_quit_clicked"          then lambda { |widget| app_quit(widget) } 
        when "on_window_subdivx_destroy"       then lambda { |widget| app_quit(widget) }
        when "on_button_search_clicked"        then lambda { |widget| on_button_search_clicked(widget) }
        when "on_button_next_clicked"          then lambda { |widget| on_button_next_clicked(widget) }
        when "on_button_clear_clicked"         then lambda { |widget| on_button_clear_clicked(widget) }
        when "on_button_results_fetch_clicked" then lambda { |widget| on_button_results_fetch_clicked(widget) }
      end
    end

    @win = @gtk.get_object("window_subdivx")
    @win.maximize

    @entry_search = @gtk.get_object("entry_search")

    @treeview_results = @gtk.get_object("treeview_results")

    column = Gtk::TreeViewColumn.new("Name", Gtk::CellRendererText.new, :text => 1)
    column.expand = false
    @treeview_results.append_column(column)

    column = Gtk::TreeViewColumn.new("CDs", Gtk::CellRendererText.new, :text => 3)
    column.expand = false
    @treeview_results.append_column(column)

    column = Gtk::TreeViewColumn.new("Description", Gtk::CellRendererText.new, :text => 2)
    column.expand = false
    @treeview_results.append_column(column)

    @treeview_results.set_tooltip_column(2)

    @liststore_results = @gtk.get_object("liststore_results")
    
    @button_next = @gtk.get_object("button_next")
    @button_next.sensitive = false
    @button_clear = @gtk.get_object("button_clear")
    @button_clear.sensitive = false
    @button_search = @gtk.get_object("button_search")
    @button_search.sensitive = true

    @label_results = @gtk.get_object("label_results")
    
    @page = 1
  end
  
  def run
    @win.show
    Gtk.main
  end
  
  private
  
  def app_quit(widget)
    Gtk.main_quit
  end
  
  def on_button_search_clicked(widget)
    if @entry_search.text.strip.size > 0
      @entry_search.sensitive = false
      @button_search.sensitive = false
      @button_next.sensitive = true
      @button_clear.sensitive = true
      @label_results.text = "Results Page #{@page}"
      @liststore_results.clear
      results = @subdivxclient.search(@entry_search.text.strip, @page)
      results.each_with_index do |result, i|
        row = @liststore_results.append
        row[0] = i
        row[1] = CGI.escapeHTML(result[:title])
        row[2] = CGI.escapeHTML(result[:description])
        row[3] = result[:cds]
        row[4] = result[:link]
      end
      if results.size < 20
        @button_next.sensitive = false
      end
    else
      dialog = Gtk::MessageDialog.new(@win, Gtk::Dialog::DESTROY_WITH_PARENT, Gtk::MessageDialog::ERROR, Gtk::MessageDialog::BUTTONS_CLOSE)
      dialog.title = "Error Searching"
      dialog.text = "Search Was Not Performed"
      dialog.secondary_text = "You didn't specify any search terms.\nPlease try again."
      dialog.run
      dialog.destroy      
    end
  end
  
  def on_button_next_clicked(widget)
    @page += 1
    on_button_search_clicked(widget)
  end
  
  def on_button_clear_clicked(widget)
    @page = 1
    @liststore_results.clear
    @entry_search.sensitive = true
    @button_search.sensitive = true
    @button_next.sensitive = false
    @button_clear.sensitive = false
    @label_results.text = "Results"
  end
  
  def on_button_results_fetch_clicked(widget)
    if @treeview_results.selection.selected
      system("gnome-open #{@subdivxclient.fetch(@treeview_results.selection.selected[0])}")
    else
      dialog = Gtk::MessageDialog.new(@win, Gtk::Dialog::DESTROY_WITH_PARENT, Gtk::MessageDialog::ERROR, Gtk::MessageDialog::BUTTONS_CLOSE)
      dialog.title = "Error Downloading"
      dialog.text = "No Result Selected"
      dialog.secondary_text = "You have to select a result to download.\nPlease try again."
      dialog.run
      dialog.destroy
    end
  end
  
end

SubDivXGUI.new.run

exit 0

# M/#]X;6P@=F5R<VEO;CTB,2XP(C\^"CQI;G1E<F9A8V4^"B`@/')E<75I<F5S
# M(&QI8CTB9W1K*R(@=F5R<VEO;CTB,BXQ-B(O/@H@(#PA+2T@:6YT97)F86-E
# M+6YA;6EN9RUP;VQI8WD@<')O:F5C="UW:61E("TM/@H@(#QO8FIE8W0@8VQA
# M<W,](D=T:TQI<W13=&]R92(@:60](FQI<W1S=&]R95]F:6QE<R(^"B`@("`\
# M8V]L=6UN<SX*("`@("`@/"$M+2!C;VQU;6XM;F%M92!&:6QE("TM/@H@("`@
# M("`\8V]L=6UN('1Y<&4](F=C:&%R(B\^"B`@("`\+V-O;'5M;G,^"B`@/"]O
# M8FIE8W0^"B`@/&]B:F5C="!C;&%S<STB1W1K3&ES=%-T;W)E(B!I9#TB;&ES
# M='-T;W)E7W)E<W5L=',B/@H@("`@/&-O;'5M;G,^"B`@("`@(#PA+2T@8V]L
# M=6UN+6YA;64@240@+2T^"B`@("`@(#QC;VQU;6X@='EP93TB9VEN="(O/@H@
# M("`@("`\(2TM(&-O;'5M;BUN86UE($YA;64@+2T^"B`@("`@(#QC;VQU;6X@
# M='EP93TB9V-H87)A<G)A>2(O/@H@("`@("`\(2TM(&-O;'5M;BUN86UE($1E
# M<V-R:7!T:6]N("TM/@H@("`@("`\8V]L=6UN('1Y<&4](F=C:&%R87)R87DB
# M+SX*("`@("`@/"$M+2!C;VQU;6XM;F%M92!#1',@+2T^"B`@("`@(#QC;VQU
# M;6X@='EP93TB9VEN="(O/@H@("`@("`\(2TM(&-O;'5M;BUN86UE($QI;FL@
# M+2T^"B`@("`@(#QC;VQU;6X@='EP93TB9V-H87)A<G)A>2(O/@H@("`@/"]C
# M;VQU;6YS/@H@(#PO;V)J96-T/@H@(#QO8FIE8W0@8VQA<W,](D=T:U=I;F1O
# M=R(@:60](G=I;F1O=U]S=6)D:79X(CX*("`@(#QP<F]P97)T>2!N86UE/2)B
# M;W)D97)?=VED=&@B/C$P/"]P<F]P97)T>3X*("`@(#QP<F]P97)T>2!N86UE
# M/2)W:6YD;W=?<&]S:71I;VXB/F-E;G1E<CPO<')O<&5R='D^"B`@("`\<')O
# M<&5R='D@;F%M93TB9&5F875L=%]W:61T:"(^-S`P/"]P<F]P97)T>3X*("`@
# M(#QP<F]P97)T>2!N86UE/2)D969A=6QT7VAE:6=H="(^-#4P/"]P<F]P97)T
# M>3X*("`@(#QP<F]P97)T>2!N86UE/2)I8V]N7VYA;64B/FEN<V5R="UT97AT
# M/"]P<F]P97)T>3X*("`@(#QS:6=N86P@;F%M93TB9&5S=')O>2(@:&%N9&QE
# M<CTB;VY?=VEN9&]W7W-U8F1I=GA?9&5S=')O>2(O/@H@("`@/&-H:6QD/@H@
# M("`@("`\;V)J96-T(&-L87-S/2)'=&M60F]X(B!I9#TB=F)O>%]A<'`B/@H@
# M("`@("`@(#QP<F]P97)T>2!N86UE/2)V:7-I8FQE(CY4<G5E/"]P<F]P97)T
# M>3X*("`@("`@("`\<')O<&5R='D@;F%M93TB;W)I96YT871I;VXB/G9E<G1I
# M8V%L/"]P<F]P97)T>3X*("`@("`@("`\<')O<&5R='D@;F%M93TB<W!A8VEN
# M9R(^,3`\+W!R;W!E<G1Y/@H@("`@("`@(#QC:&EL9#X*("`@("`@("`@(#QO
# M8FIE8W0@8VQA<W,](D=T:TA";W@B(&ED/2)H8F]X7W-E87)C:"(^"B`@("`@
# M("`@("`@(#QP<F]P97)T>2!N86UE/2)V:7-I8FQE(CY4<G5E/"]P<F]P97)T
# M>3X*("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](G-P86-I;F<B/C$P/"]P
# M<F]P97)T>3X*("`@("`@("`@("`@/&-H:6QD/@H@("`@("`@("`@("`@(#QO
# M8FIE8W0@8VQA<W,](D=T:TQA8F5L(B!I9#TB;&%B96Q?<V5A<F-H(CX*("`@
# M("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)V:7-I8FQE(CY4<G5E/"]P
# M<F]P97)T>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)L86)E
# M;"(@=')A;G-L871A8FQE/2)Y97,B/E-E87)C:"!?5&5R;7,Z/"]P<F]P97)T
# M>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)U<V5?=6YD97)L
# M:6YE(CY4<G5E/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T
# M>2!N86UE/2)M;F5M;VYI8U]W:61G970B/F5N=')Y7W-E87)C:#PO<')O<&5R
# M='D^"B`@("`@("`@("`@("`@/"]O8FIE8W0^"B`@("`@("`@("`@("`@/'!A
# M8VMI;F<^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB97AP86YD
# M(CY&86QS93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@
# M;F%M93TB9FEL;"(^1F%L<V4\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@
# M/'!R;W!E<G1Y(&YA;64](G!O<VET:6]N(CXP/"]P<F]P97)T>3X*("`@("`@
# M("`@("`@("`\+W!A8VMI;F<^"B`@("`@("`@("`@(#PO8VAI;&0^"B`@("`@
# M("`@("`@(#QC:&EL9#X*("`@("`@("`@("`@("`\;V)J96-T(&-L87-S/2)'
# M=&M%;G1R>2(@:60](F5N=')Y7W-E87)C:"(^"B`@("`@("`@("`@("`@("`\
# M<')O<&5R='D@;F%M93TB=FES:6)L92(^5')U93PO<')O<&5R='D^"B`@("`@
# M("`@("`@("`@("`\<')O<&5R='D@;F%M93TB8V%N7V9O8W5S(CY4<G5E/"]P
# M<F]P97)T>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)I;G9I
# M<VEB;&5?8VAA<B(^)B-X,C5#1CL\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@
# M(#PO;V)J96-T/@H@("`@("`@("`@("`@(#QP86-K:6YG/@H@("`@("`@("`@
# M("`@("`@/'!R;W!E<G1Y(&YA;64](G!O<VET:6]N(CXQ/"]P<F]P97)T>3X*
# M("`@("`@("`@("`@("`\+W!A8VMI;F<^"B`@("`@("`@("`@(#PO8VAI;&0^
# M"B`@("`@("`@("`@(#QC:&EL9#X*("`@("`@("`@("`@("`\;V)J96-T(&-L
# M87-S/2)'=&M"=71T;VXB(&ED/2)B=71T;VY?<V5A<F-H(CX*("`@("`@("`@
# M("`@("`@(#QP<F]P97)T>2!N86UE/2)L86)E;"(@=')A;G-L871A8FQE/2)Y
# M97,B/E]396%R8V@@4W5B=&ET;&5S/"]P<F]P97)T>3X*("`@("`@("`@("`@
# M("`@(#QP<F]P97)T>2!N86UE/2)V:7-I8FQE(CY4<G5E/"]P<F]P97)T>3X*
# M("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)C86Y?9F]C=7,B/E1R
# M=64\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64]
# M(G)E8V5I=F5S7V1E9F%U;'0B/E1R=64\+W!R;W!E<G1Y/@H@("`@("`@("`@
# M("`@("`@/'!R;W!E<G1Y(&YA;64](FEM86=E(CYI;6%G95]F:6YD/"]P<F]P
# M97)T>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)U<V5?=6YD
# M97)L:6YE(CY4<G5E/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@(#QS:6=N
# M86P@;F%M93TB8VQI8VME9"(@:&%N9&QE<CTB;VY?8G5T=&]N7W-E87)C:%]C
# M;&EC:V5D(B\^"B`@("`@("`@("`@("`@/"]O8FIE8W0^"B`@("`@("`@("`@
# M("`@/'!A8VMI;F<^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB
# M97AP86YD(CY&86QS93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<')O
# M<&5R='D@;F%M93TB9FEL;"(^1F%L<V4\+W!R;W!E<G1Y/@H@("`@("`@("`@
# M("`@("`@/'!R;W!E<G1Y(&YA;64](G!O<VET:6]N(CXR/"]P<F]P97)T>3X*
# M("`@("`@("`@("`@("`\+W!A8VMI;F<^"B`@("`@("`@("`@(#PO8VAI;&0^
# M"B`@("`@("`@("`\+V]B:F5C=#X*("`@("`@("`@(#QP86-K:6YG/@H@("`@
# M("`@("`@("`\<')O<&5R='D@;F%M93TB97AP86YD(CY&86QS93PO<')O<&5R
# M='D^"B`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)F:6QL(CY&86QS93PO
# M<')O<&5R='D^"B`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)P;W-I=&EO
# M;B(^,#PO<')O<&5R='D^"B`@("`@("`@("`\+W!A8VMI;F<^"B`@("`@("`@
# M/"]C:&EL9#X*("`@("`@("`\8VAI;&0^"B`@("`@("`@("`\;V)J96-T(&-L
# M87-S/2)'=&M60F]X(B!I9#TB=F)O>%]R97-U;'1S7V%N9%]F:6QE<R(^"B`@
# M("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)V:7-I8FQE(CY4<G5E/"]P<F]P
# M97)T>3X*("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](F]R:65N=&%T:6]N
# M(CYV97)T:6-A;#PO<')O<&5R='D^"B`@("`@("`@("`@(#QP<F]P97)T>2!N
# M86UE/2)S<&%C:6YG(CXQ,#PO<')O<&5R='D^"B`@("`@("`@("`@(#QC:&EL
# M9#X*("`@("`@("`@("`@("`\;V)J96-T(&-L87-S/2)'=&M,86)E;"(@:60]
# M(FQA8F5L7W)E<W5L=',B/@H@("`@("`@("`@("`@("`@/'!R;W!E<G1Y(&YA
# M;64](G9I<VEB;&4B/E1R=64\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@
# M/'!R;W!E<G1Y(&YA;64](GAA;&EG;B(^,#PO<')O<&5R='D^"B`@("`@("`@
# M("`@("`@("`\<')O<&5R='D@;F%M93TB;&%B96PB('1R86YS;&%T86)L93TB
# M>65S(CY?4F5S=6QT<SPO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<')O
# M<&5R='D@;F%M93TB=7-E7W5N9&5R;&EN92(^5')U93PO<')O<&5R='D^"B`@
# M("`@("`@("`@("`@/"]O8FIE8W0^"B`@("`@("`@("`@("`@/'!A8VMI;F<^
# M"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB97AP86YD(CY&86QS
# M93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB
# M9FEL;"(^1F%L<V4\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@/'!R;W!E
# M<G1Y(&YA;64](G!O<VET:6]N(CXP/"]P<F]P97)T>3X*("`@("`@("`@("`@
# M("`\+W!A8VMI;F<^"B`@("`@("`@("`@(#PO8VAI;&0^"B`@("`@("`@("`@
# M(#QC:&EL9#X*("`@("`@("`@("`@("`\;V)J96-T(&-L87-S/2)'=&M38W)O
# M;&QE9%=I;F1O=R(@:60](G-C<F]L;&5D=VEN9&]W7W)E<W5L=',B/@H@("`@
# M("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](G9I<VEB;&4B/E1R=64\+W!R
# M;W!E<G1Y/@H@("`@("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](F-A;E]F
# M;V-U<R(^5')U93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<')O<&5R
# M='D@;F%M93TB:'-C<F]L;&)A<E]P;VQI8WDB/F%U=&]M871I8SPO<')O<&5R
# M='D^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB=G-C<F]L;&)A
# M<E]P;VQI8WDB/F%U=&]M871I8SPO<')O<&5R='D^"B`@("`@("`@("`@("`@
# M("`\8VAI;&0^"B`@("`@("`@("`@("`@("`@(#QO8FIE8W0@8VQA<W,](D=T
# M:U1R9656:65W(B!I9#TB=')E979I97=?<F5S=6QT<R(^"B`@("`@("`@("`@
# M("`@("`@("`@/'!R;W!E<G1Y(&YA;64](G9I<VEB;&4B/E1R=64\+W!R;W!E
# M<G1Y/@H@("`@("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)C86Y?
# M9F]C=7,B/E1R=64\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@("`@(#QP
# M<F]P97)T>2!N86UE/2)M;V1E;"(^;&ES='-T;W)E7W)E<W5L=',\+W!R;W!E
# M<G1Y/@H@("`@("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)S96%R
# M8VA?8V]L=6UN(CXP/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@("`@("`\
# M<')O<&5R='D@;F%M93TB=&]O;'1I<%]C;VQU;6XB/C(\+W!R;W!E<G1Y/@H@
# M("`@("`@("`@("`@("`@("`\+V]B:F5C=#X*("`@("`@("`@("`@("`@(#PO
# M8VAI;&0^"B`@("`@("`@("`@("`@/"]O8FIE8W0^"B`@("`@("`@("`@("`@
# M/'!A8VMI;F<^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB<&]S
# M:71I;VXB/C$\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@(#PO<&%C:VEN9SX*
# M("`@("`@("`@("`@/"]C:&EL9#X*("`@("`@("`@("`@/&-H:6QD/@H@("`@
# M("`@("`@("`@(#QO8FIE8W0@8VQA<W,](D=T:TA";W@B(&ED/2)H8F]X,2(^
# M"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB=FES:6)L92(^5')U
# M93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB
# M<W!A8VEN9R(^,3`\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@/&-H:6QD
# M/@H@("`@("`@("`@("`@("`@("`\;V)J96-T(&-L87-S/2)'=&M"=71T;VXB
# M(&ED/2)B=71T;VY?;F5X="(^"B`@("`@("`@("`@("`@("`@("`@/'!R;W!E
# M<G1Y(&YA;64](FQA8F5L(B!T<F%N<VQA=&%B;&4](GEE<R(^1F5T8V@@7TYE
# M>'0@4&%G93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`@("`@/'!R;W!E
# M<G1Y(&YA;64](G9I<VEB;&4B/E1R=64\+W!R;W!E<G1Y/@H@("`@("`@("`@
# M("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)C86Y?9F]C=7,B/E1R=64\+W!R
# M;W!E<G1Y/@H@("`@("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)R
# M96-E:79E<U]D969A=6QT(CY4<G5E/"]P<F]P97)T>3X*("`@("`@("`@("`@
# M("`@("`@("`\<')O<&5R='D@;F%M93TB:6UA9V4B/FEM86=E7VYE>'0\+W!R
# M;W!E<G1Y/@H@("`@("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)U
# M<V5?=6YD97)L:6YE(CY4<G5E/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@
# M("`@("`\<VEG;F%L(&YA;64](F-L:6-K960B(&AA;F1L97(](F]N7V)U='1O
# M;E]N97AT7V-L:6-K960B+SX*("`@("`@("`@("`@("`@("`@/"]O8FIE8W0^
# M"B`@("`@("`@("`@("`@("`@(#QP86-K:6YG/@H@("`@("`@("`@("`@("`@
# M("`@(#QP<F]P97)T>2!N86UE/2)P;W-I=&EO;B(^,#PO<')O<&5R='D^"B`@
# M("`@("`@("`@("`@("`@(#PO<&%C:VEN9SX*("`@("`@("`@("`@("`@(#PO
# M8VAI;&0^"B`@("`@("`@("`@("`@("`\8VAI;&0^"B`@("`@("`@("`@("`@
# M("`@(#QO8FIE8W0@8VQA<W,](D=T:T)U='1O;B(@:60](F)U='1O;E]C;&5A
# M<B(^"B`@("`@("`@("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](FQA8F5L
# M(B!T<F%N<VQA=&%B;&4](GEE<R(^7T-L96%R(%-E87)C:#PO<')O<&5R='D^
# M"B`@("`@("`@("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](G9I<VEB;&4B
# M/E1R=64\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@("`@(#QP<F]P97)T
# M>2!N86UE/2)C86Y?9F]C=7,B/E1R=64\+W!R;W!E<G1Y/@H@("`@("`@("`@
# M("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)R96-E:79E<U]D969A=6QT(CY4
# M<G5E/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@("`@("`\<')O<&5R='D@
# M;F%M93TB:6UA9V4B/FEM86=E7W)E<V5T/"]P<F]P97)T>3X*("`@("`@("`@
# M("`@("`@("`@("`\<')O<&5R='D@;F%M93TB=7-E7W5N9&5R;&EN92(^5')U
# M93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`@("`@/'-I9VYA;"!N86UE
# M/2)C;&EC:V5D(B!H86YD;&5R/2)O;E]B=71T;VY?8VQE87)?8VQI8VME9"(O
# M/@H@("`@("`@("`@("`@("`@("`\+V]B:F5C=#X*("`@("`@("`@("`@("`@
# M("`@/'!A8VMI;F<^"B`@("`@("`@("`@("`@("`@("`@/'!R;W!E<G1Y(&YA
# M;64](G!O<VET:6]N(CXQ/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@("`@
# M/"]P86-K:6YG/@H@("`@("`@("`@("`@("`@/"]C:&EL9#X*("`@("`@("`@
# M("`@("`\+V]B:F5C=#X*("`@("`@("`@("`@("`\<&%C:VEN9SX*("`@("`@
# M("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)E>'!A;F0B/D9A;'-E/"]P<F]P
# M97)T>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)F:6QL(CY&
# M86QS93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M
# M93TB<&]S:71I;VXB/C(\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@(#PO<&%C
# M:VEN9SX*("`@("`@("`@("`@/"]C:&EL9#X*("`@("`@("`@("`@/&-H:6QD
# M/@H@("`@("`@("`@("`@(#QO8FIE8W0@8VQA<W,](D=T:T)U='1O;B(@:60]
# M(F)U='1O;E]R97-U;'1S7V9E=&-H(CX*("`@("`@("`@("`@("`@(#QP<F]P
# M97)T>2!N86UE/2)L86)E;"(@=')A;G-L871A8FQE/2)Y97,B/E]$;W=N;&]A
# M9"!396QE8W1E9"!297-U;'0\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@
# M/'!R;W!E<G1Y(&YA;64](G9I<VEB;&4B/E1R=64\+W!R;W!E<G1Y/@H@("`@
# M("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](F-A;E]F;V-U<R(^5')U93PO
# M<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB<F5C
# M96EV97-?9&5F875L="(^5')U93PO<')O<&5R='D^"B`@("`@("`@("`@("`@
# M("`\<')O<&5R='D@;F%M93TB:6UA9V4B/FEM86=E7V9E=&-H/"]P<F]P97)T
# M>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)U<V5?=6YD97)L
# M:6YE(CY4<G5E/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@(#QS:6=N86P@
# M;F%M93TB8VQI8VME9"(@:&%N9&QE<CTB;VY?8G5T=&]N7W)E<W5L='-?9F5T
# M8VA?8VQI8VME9"(O/@H@("`@("`@("`@("`@(#PO;V)J96-T/@H@("`@("`@
# M("`@("`@(#QP86-K:6YG/@H@("`@("`@("`@("`@("`@/'!R;W!E<G1Y(&YA
# M;64](F5X<&%N9"(^1F%L<V4\+W!R;W!E<G1Y/@H@("`@("`@("`@("`@("`@
# M/'!R;W!E<G1Y(&YA;64](F9I;&PB/D9A;'-E/"]P<F]P97)T>3X*("`@("`@
# M("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)P;W-I=&EO;B(^,SPO<')O<&5R
# M='D^"B`@("`@("`@("`@("`@/"]P86-K:6YG/@H@("`@("`@("`@("`\+V-H
# M:6QD/@H@("`@("`@("`@/"]O8FIE8W0^"B`@("`@("`@("`\<&%C:VEN9SX*
# M("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](G!O<VET:6]N(CXQ/"]P<F]P
# M97)T>3X*("`@("`@("`@(#PO<&%C:VEN9SX*("`@("`@("`\+V-H:6QD/@H@
# M("`@("`@(#QC:&EL9#X*("`@("`@("`@(#QO8FIE8W0@8VQA<W,](D=T:TA"
# M=71T;VY";W@B(&ED/2)H8G5T=&]N8F]X7V%C=&EO;G,B/@H@("`@("`@("`@
# M("`\<')O<&5R='D@;F%M93TB=FES:6)L92(^5')U93PO<')O<&5R='D^"B`@
# M("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)L87EO=71?<W1Y;&4B/F5N9#PO
# M<')O<&5R='D^"B`@("`@("`@("`@(#QC:&EL9#X*("`@("`@("`@("`@("`\
# M;V)J96-T(&-L87-S/2)'=&M"=71T;VXB(&ED/2)B=71T;VY?<75I="(^"B`@
# M("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB;&%B96PB('1R86YS;&%T
# M86)L93TB>65S(CY%7WAI=#PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\
# M<')O<&5R='D@;F%M93TB=FES:6)L92(^5')U93PO<')O<&5R='D^"B`@("`@
# M("`@("`@("`@("`\<')O<&5R='D@;F%M93TB8V%N7V9O8W5S(CY4<G5E/"]P
# M<F]P97)T>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)R96-E
# M:79E<U]D969A=6QT(CY4<G5E/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@
# M(#QP<F]P97)T>2!N86UE/2)I;6%G92(^:6UA9V5?97AI=#PO<')O<&5R='D^
# M"B`@("`@("`@("`@("`@("`\<')O<&5R='D@;F%M93TB=7-E7W5N9&5R;&EN
# M92(^5')U93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\<VEG;F%L(&YA
# M;64](F-L:6-K960B(&AA;F1L97(](F]N7V)U='1O;E]Q=6ET7V-L:6-K960B
# M+SX*("`@("`@("`@("`@("`\+V]B:F5C=#X*("`@("`@("`@("`@("`\<&%C
# M:VEN9SX*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N86UE/2)E>'!A;F0B
# M/D9A;'-E/"]P<F]P97)T>3X*("`@("`@("`@("`@("`@(#QP<F]P97)T>2!N
# M86UE/2)F:6QL(CY&86QS93PO<')O<&5R='D^"B`@("`@("`@("`@("`@("`\
# M<')O<&5R='D@;F%M93TB<&]S:71I;VXB/C`\+W!R;W!E<G1Y/@H@("`@("`@
# M("`@("`@(#PO<&%C:VEN9SX*("`@("`@("`@("`@/"]C:&EL9#X*("`@("`@
# M("`@(#PO;V)J96-T/@H@("`@("`@("`@/'!A8VMI;F<^"B`@("`@("`@("`@
# M(#QP<F]P97)T>2!N86UE/2)E>'!A;F0B/D9A;'-E/"]P<F]P97)T>3X*("`@
# M("`@("`@("`@/'!R;W!E<G1Y(&YA;64](F9I;&PB/D9A;'-E/"]P<F]P97)T
# M>3X*("`@("`@("`@("`@/'!R;W!E<G1Y(&YA;64](G!O<VET:6]N(CXR/"]P
# M<F]P97)T>3X*("`@("`@("`@(#PO<&%C:VEN9SX*("`@("`@("`\+V-H:6QD
# M/@H@("`@("`\+V]B:F5C=#X*("`@(#PO8VAI;&0^"B`@/"]O8FIE8W0^"B`@
# M/&]B:F5C="!C;&%S<STB1W1K26UA9V4B(&ED/2)I;6%G95]F:6YD(CX*("`@
# M(#QP<F]P97)T>2!N86UE/2)V:7-I8FQE(CY4<G5E/"]P<F]P97)T>3X*("`@
# M(#QP<F]P97)T>2!N86UE/2)S=&]C:R(^9W1K+69I;F0\+W!R;W!E<G1Y/@H@
# M(#PO;V)J96-T/@H@(#QO8FIE8W0@8VQA<W,](D=T:TEM86=E(B!I9#TB:6UA
# M9V5?97AI="(^"B`@("`\<')O<&5R='D@;F%M93TB=FES:6)L92(^5')U93PO
# M<')O<&5R='D^"B`@("`\<')O<&5R='D@;F%M93TB<W1O8VLB/F=T:RUQ=6ET
# M/"]P<F]P97)T>3X*("`\+V]B:F5C=#X*("`\;V)J96-T(&-L87-S/2)'=&M)
# M;6%G92(@:60](FEM86=E7V9E=&-H(CX*("`@(#QP<F]P97)T>2!N86UE/2)V
# M:7-I8FQE(CY4<G5E/"]P<F]P97)T>3X*("`@(#QP<F]P97)T>2!N86UE/2)S
# M=&]C:R(^9W1K+6=O=&\M8F]T=&]M/"]P<F]P97)T>3X*("`\+V]B:F5C=#X*
# M("`\;V)J96-T(&-L87-S/2)'=&M);6%G92(@:60](FEM86=E7VYE>'0B/@H@
# M("`@/'!R;W!E<G1Y(&YA;64](G9I<VEB;&4B/E1R=64\+W!R;W!E<G1Y/@H@
# M("`@/'!R;W!E<G1Y(&YA;64](G-T;V-K(CYG=&LM9V\M9F]R=V%R9#PO<')O
# M<&5R='D^"B`@/"]O8FIE8W0^"B`@/&]B:F5C="!C;&%S<STB1W1K26UA9V4B
# M(&ED/2)I;6%G95]R97-E="(^"B`@("`\<')O<&5R='D@;F%M93TB=FES:6)L
# M92(^5')U93PO<')O<&5R='D^"B`@("`\<')O<&5R='D@;F%M93TB<W1O8VLB
# M/F=T:RUC;&5A<CPO<')O<&5R='D^"B`@/"]O8FIE8W0^"CPO:6YT97)F86-E
# "/@H`
# `

