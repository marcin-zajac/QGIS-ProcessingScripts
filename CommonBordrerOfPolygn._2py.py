from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingOutputNumber,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsVectorLayer,
                       QgsGeometry,
                       QgsFeature,
                       QgsProcessingParameterFeatureSink,
                       QgsProject,
                       QgsFeatureSink)
import processing
import itertools

class CommonBordrerOfPolygn(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer,
    creates some new layers and returns some results.
    """
    INPUT = 'INPUT_VECTOR'
    OUTPUT='OUTPUT'
    

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        # Must return a new copy of your algorithm.
        return CommonBordrerOfPolygn()

    def name(self):
        """
        Returns the unique algorithm name.
        """
        return 'bufferrasterextend'

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return self.tr('Wspólne granice poligonów')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return self.tr('Zwraca wspólne granice stykających się poligonów jako linie')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs
        to.
        """
        return 'commonborderofpolygon'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return self.tr('Wspólne granice poligonów')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and outputs of the algorithm.
        """
        # 'INPUT' is the recommended name for the main input
        # parameter.
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT, 'Input vector:'))
        
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, 'Warstwa wynikowa'))
        


        # 'OUTPUT' is the recommended name for the main output
        # parameter.



    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # First, we get the count of features from the INPUT layer.
        # This layer is defined as a QgsProcessingParameterFeatureSource
        # parameter, so it is retrieved by calling
        # self.parameterAsSource.

        source = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        numfeatures = source.featureCount()

        common_borders = QgsVectorLayer("MultiLineString?crs=epsg:2180", "common_brd",'memory')
        common_borders.startEditing()

        rings = [QgsGeometry().fromPolylineXY(elem.geometry().asPolygon()[0]) for elem in source.getFeatures()]

        for i in itertools.combinations(rings, 2):
            if i[0].intersects(i[1]):
                wkt = i[0].intersection(i[1]).asWkt()
                geom = QgsGeometry()
                geom = QgsGeometry.fromWkt(wkt)
                feat = QgsFeature()
                feat.setGeometry(geom)
                common_borders.dataProvider().addFeatures([feat])
                print(feat.id())
                
        common_borders.commitChanges()
        QgsProject.instance().addMapLayer(common_borders)
        for f in common_borders.getFeatures():
            print("sssssssss", f.id())
                
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
        common_borders.fields(), common_borders.wkbType(), source.sourceCrs())
        
        for fe in common_borders.getFeatures():
            sink.addFeature(fe, QgsFeatureSink.FastInsert)
     
        print("ddddddddddddddddddddddddddddddddddd")
        if feedback.isCanceled():
            return {}


        # Return the results
        return {'OUTPUT': dest_id,
                'NUMBEROFFEATURES': numfeatures}