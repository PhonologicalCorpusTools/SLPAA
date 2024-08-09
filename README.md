For a demonstration of how the software will work, please see: <a href="https://www.youtube.com/watch?v=o4C4hibTW1o"> SLP-AA Initial Demonstration Video on YouTube</a>

Detailed documentation is available on ReadTheDocs: [https://slp-aa.readthedocs.io](https://slp-aa.readthedocs.io/)

# SLP-Annotator/Analyzer

Sign Language Phonetic-Annotator/Analyzer (SLP-AA) is a graphical user interface (GUI)-based software system for the form-based transcription and analysis of signs. The system is intended to be relatively phonetic in nature and compatible with multiple phonological theories, enabling transcription of detailed variation across many sign languages, but largely without relying on a specific notation system. 

There are two primary components to the SLP-AA software: the annotator portion and the analyzer portion. Both components make use of a relatively straightforward graphical user interface that involves selecting from pre-set options written out in text in most cases, to maximize consistency and efficiency of coding.

The annotator portion includes or will include modules for coding meta information and for transcribing sign type, movement, location, contact, hand configuration, orientation, and non-manual components. Additionally, temporal relations among these modules can be encoded using a generic ‘x-slot’ framework. There is also some ability for the software to auto-generate, auto-fill, and auto-link components. Inspiration for the coding systems comes from a variety of sources, including especially Crasborn 2001; Brentari 1998; van der Kooij 2002; Johnson & Liddell 2011a-c & 2012; and Morgan 2017. See also Tkachman et al. 2016, Hall et al. 2017, and Lo & Hall 2019 for descriptions of earlier versions of the software.

The analyzer interface, intended to facilitate phonological searches and analyses is modelled on the _Phonological CorpusTools_ software for spoken languages (Hall et al. 2019). It will allow users to search for any (combination of) specifications within the detailed coding, as well as to search for categories of signs that span specific combinations (e.g., searching for signs with three extended fingers, regardless of which fingers those are, or searching for multi-syllabic signs defined in a number of different ways). We also intend to have several pre-set search options (e.g., searching for dominance condition violations or searching for typologically rare properties). In addition to the searches, other phonological analyses will be possible. For example, these might include finding minimal pairs, calculating the neighbourhood density of a given sign (Luce & Pisoni 1998, Yao 2011), calculating the functional load (Hockett 1966, Surendran & Niyogi 2003) or informativity (Cohen Priva 2015) of a particular phonological component, etc. Finally, we envision having a side-by-side comparison option, which will highlight form-based similarities or differences between signs selected by the user.

Currently, SLP-AA is a stand-alone piece of software that can be used to give detailed phonetic transcriptions of individual signs, one at a time. While these signs can come from any source, the software does not currently directly allow for the transcription of continuous signing. 

The handshape fonts are created by <a href="http://www.cslds.org/v4/resources.php?id=1">CSLDS, CUHK</a>.

See a list of our [contributors](CONTRIBUTORS.md).

References:

Brentari, D. (1998). A Prosodic Model of Sign Language Phonology. Cambridge, MA: MIT Press.

Caselli, N., Sevcikova, Z., Cohen-Goldberg, A., Emmorey, K. (2016). ASL-Lex: A lexical database for ASL. Behavior Research Methods. doi:10.3758/s13428-016-0742-0.

Cohen Priva, U. (2015). Informativity affects consonant duration and deletion rates. Laboratory Phonology, 6(2), pp. 243-278.

Crasborn, O. (2001). Phonetic implementation of phonological categories in Sign Language of the Netherlands. Doctoral dissertation. Universiteit Leiden.

Hall, K. C., Mackie, S., Fry, M. & Tkachman, O. (2017). SLPAnnotator: Tools for implementing Sign Language Phonetic Annotation. In Proceedings of the 18th Annual Conference of the International Speech Communication Association (INTERSPEECH 2017). Stockholm, Sweden: International Speech Communication Association, pp. 2083-2087.

Hall, K. C., Mackie, J. S. & Lo, R. Y-H. (2019). Phonological Corpus Tools: Software for doing phonological analysis on transcribed corpora. International Journal of Corpus Linguistics, 24(4), pp. 522-535.

Hockett, C. F. (1966). The Quantification of functional load: A linguistic problem. U.S. Air Force Memorandum RM-5168-PR.

Johnson, Robert E. & Scott K. Liddell. 2010. Toward a phonetic representation of signs: Sequentiality and contrast. Sign Language Studies 11.241-74.

Johnson, Robert E. & Scott K. Liddell. 2011a. A segmental framework for representing signs phonetically. Sign Language Studies 11.408-63.

Johnson, Robert E. & Scott K. Liddell. 2011b. Toward a Phonetic Representation of Hand Configuration: The fingers. Sign Language Studies 12.5-45.

Johnson, Robert E. & Scott K. Liddell. 2012. Toward a Phonetic Representation of Hand Configuration: The thumb. Sign Language Studies 12.316-33.

Kooij, E. van der (2002). Phonological categories in Sign Language of the Netherlands: The role of phonetic implementation and iconicity. Doctoral dissertation. Netherlands Graduate School of Linguistics.

Luce, P. A. & Pisoni, D. B. (1998). Recognizing spoken words: The neighborhood activation model. Ear and Hearing, 19, pp. 1-36.

Morgan, H. E. (2017). The phonology of Kenyan Sign Language (southwestern dialect). Doctoral dissertation. University of California, San Diego.

Surendran, D. and Niyogi, P. (2003). Measuring the usefulness (functional load) of phonological contrasts. Technical Report TR-2003–12, Department of Computer Science, University of Chicago.

Tkachman, Oksana, Kathleen Currie Hall, André Xavier & Bryan Gick. 2016. Sign Language Phonetic Annotation meets Phonological CorpusTools: Towards a sign language toolset for phonetic notation and phonological analysis. Proceedings of the Annual Meeting of Phonology.

Yao, Y. (2011). The effects of phonological neighborhoods on pronunciation variation in conversational speech. Doctoral dissertation. University of California Berkeley.

