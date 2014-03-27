""" Merge all the images in icons/* into one big file.
Create a CSS file so that we can easily display them.
"""
import Image
import glob

MaxWidth = 40
MaxHeight = 40

images = []
total_height = 0
largest_width = 0

for img_file in glob.glob("icons/*.png"):
    print "Loading %s" % img_file
    img = Image.open(img_file)

    if img.size[0] > largest_width:
        largest_width = img.size[0]

    total_height += img.size[1] + 10

    # extract URL from path, and keep track of the image
    domain = img_file[5:-4]
    domain = domain[1:]
    
    print " %s - %s " % (domain, img_file)

    if domain == "no-logo":
        # no-logo should be the first image in the list
        images.insert(0, (domain, img))
    else:
        images.append((domain, img))

big_image = Image.new("RGBA", (largest_width, total_height))
current_height_offset = 0

css_output = []
each_selector_properties = ""  

for domain, img in images:
    # add the dimensions to the css selector just if they are different of 40x40
    each_selector_properties = "{"
    
    if MaxWidth != img.size[0]:
        each_selector_properties += """ 
    width: %dpx;""" % img.size[0];
    if MaxHeight != img.size[1]:
        each_selector_properties += """ 
    height: %dpx;""" % img.size[1] + 5;
    
    each_selector_properties += """
    background-position: 0px %dpx;
}
""" % (big_image.size[1] - current_height_offset)

    css_output.append((domain,each_selector_properties))
    
    big_image.paste(img, (0, current_height_offset))
    current_height_offset += img.size[1] + 10

big_image.save("source-logos.png")

with open("../square-source-logos.css", "w") as css_file:

    print total_height
    css_file.write(""".thumbnail .source-image .icon{
      background-image: url("imgs/source-logos.png");
      display: inline-block;
      height: 40px;
      width: 40px;
      display: inline-block;
      background-position: 0% 0%; 
}
""")

    for domain, css in css_output:
        print "outputting %s" % domain

        if domain == "no-logo":
            continue

        css_file.write(".source-image.source-%s .icon %s" %
                       (domain.replace(".", "-"), css))
