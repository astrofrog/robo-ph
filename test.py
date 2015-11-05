from roboph import Abstract, VOICES

abstract = Abstract()
abstract.title = "Limits on Lyman Continuum escape from z=2.2 H-alpha emitting galaxies"
abstract.authors = ["A. Sandberg", "G. Ostlin", "J. Melinder", "A. Bik", "L. Guaita"]
abstract.subjects = ["GA"]
abstract.text = """
The leakage of Lyman continuum photons from star forming galaxies is an
elusive parameter. When observed, it provides a wealth of information on star
formation in galaxies and the geometry of the interstellar medium, and puts
constraints on the role of star forming galaxies in the reionization of the
universe. H-alpha-selected galaxies at z~2 trace the highest star formation
population at the peak of cosmic star formation history, providing a base for
directly measuring Lyman continuum escape. Here we present this method, and
highlight its benefits as well as caveats. We also use the method on 10
H-alpha emitters in the Chandra Deep Field South at z=2.2, also imaged with
the Hubble Space Telescope in the ultraviolet. We find no individual Lyman
continuum detections, and our stack puts a 5 sigma upper limit on the average
absolute escape fraction of <24%, consistent with similar studies. With
future planned observations, the sample sizes would rapidly increase and the
method presented here would provide very robust constraints on the escape
fraction.
"""

abstract.to_audio('lyman.mp3', voice='fiona.premium')
