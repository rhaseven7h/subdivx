#!/usr/bin/env ruby

require 'rubygems'
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
    open("http://www.subdivx.com/bajar.php?captcha_user=ME2&idcaptcha=1007&desub=#{desub}&u=#{u}", "referer" => @results[int_num][:link]) do |h|
      fn = h.meta["content-disposition"].split(';')[1].split('=')[1]
      File.open(File.join(File.dirname(__FILE__), "cache", fn), "w") do |o|
        o.write(h.read)
      end
    end
    appdir = File.expand_path(File.dirname(__FILE__))
    return File.join(appdir, "cache", fn)
  end
  
end

class SubDivXGUI
  
  def initialize
    @subdivxclient = SubDivXClient.new
    @gtk = Gtk::Builder.new
    @gtk << File.join(File.expand_path(File.dirname(__FILE__)), "subdivx.glade")
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
      system("file-roller #{@subdivxclient.fetch(@treeview_results.selection.selected[0])}")
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


=begin
s = SubDivX.new
if ARGV[0].strip.downcase == 'search'
  s.search(ARGV[1..-1].join(' '))
  pp s.results
elsif ARGV[0].strip.downcase == 'get'
  s.search(ARGV[2..-1].join(' '))
  s.fetch(ARGV[1].to_i)
else
  puts "Specify either search or get."
end

=end
