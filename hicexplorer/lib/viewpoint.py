
import numpy as np


class Viewpoint():

    def __init__(self, pHiCMatrix=None):
        self.hicMatrix = pHiCMatrix

    def setHiCMatrixObj(self, pHiCMatrix):
        self.hicMatrix = pHiCMatrix

    def readReferencePointFile(self, pBedFile):
        viewpoints = []

        with open(pBedFile, 'r') as file:
            for line in file.readlines():
                line_ = line.split('\t')
                if len(line_) == 2:
                    chrom, start, end = line_[0], line_[1], line_[1]
                else:
                    chrom, start, end = line_
                viewpoints.append((chrom, start, end))
        return viewpoints

    def readInteractionFile(self, pBedFile):
        # use header info to store reference point, and based matrix
        data = []
        with open(pBedFile) as fh:
            header = fh.readline()
            for line in fh.readlines():
                line_ = line.split('\t')
                data.append(float(line_[-1]))
        return header, data

    def writeInteractionFile(self, pBedFile, pData, pHeader):
        with open(pBedFile + '.bed', 'w') as fh:
            fh.write('#{}\n'.format(pHeader))
            for j, interaction in enumerate(pData):
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{:.12f}\t{:.12f}\n".
                        format(toString(interaction[0]), toString(interaction[1]), toString(interaction[2]),
                            toString(interaction[3]), toString(interaction[4]),
                            toString(interaction[5]), float(interaction[6]),
                            float(average_contacts[i][j])))

    def computeViewpoint(self, pReferencePoint, pChromViewpoint, pRegion_start, pRegion_end):
        # hic = pHiCMatrix
        view_point_start, view_point_end = self.getReferencePointAsMatrixIndices(pReferencePoint)

        view_point_range = self.getViewpointRangeAsMatrixIndices(pChromViewpoint, pRegion_start, pRegion_end)
        elements_of_viewpoint = view_point_range[1] - view_point_range[0]
        data_list = np.zeros(elements_of_viewpoint)
        view_point_start_ = view_point_start
        interactions_list = None

        while view_point_start_ <= view_point_end:
            chrom, start, end, _ = hic.getBinPos(view_point_start_)
            for j, idx in zip(range(elements_of_viewpoint), range(view_point_range[0], view_point_range[1], 1)):
                data_list[j] += hic.matrix[view_point_start_, idx]
            view_point_start_ += 1

        return data_list

    def createInteractionFileData(self, pReferencePoint, pChromViewpoint, pRegion_start, pRegion_end, pInteractionData):

        view_point_start, view_point_end = self.getReferencePointAsMatrixIndices(pReferencePoint)
        view_point_range = self.getViewpointRangeAsMatrixIndices(pChromViewpoint, pRegion_start, pRegion_end)
        elements_of_viewpoint = view_point_range[1] - view_point_range[0]

        interactions_list = []
        chrom, start, _, _ = hic.getBinPos(view_point_start)
        _, _, end, _ = hic.getBinPos(view_point_end)

        for j, idx in zip(range(elements_of_viewpoint), range(view_point_range[0], view_point_range[1], 1)):
            chrom_second, start_second, end_second, _ = self.hicMatrix.getBinPos(idx)
            interactions_list.append((chrom, start, end, chrom_second, start_second, end_second, data_list[j]))

        return interactions_list

    def getViewpointRangeAsMatrixIndices(self, pChromViewpoint, pRegion_start, pRegion_end):

        return self.hicMatrix.getRegionBinRange(pChromViewpoint, pRegion_start, pRegion_end)

    def getReferencePointAsMatrixIndices(self, pReferencePoint):
        if len(pReferencePoint) == 2:
            view_point_start, view_point_end = self.hicMatrix.getRegionBinRange(pReferencePoint[0], int(pReferencePoint[1]), int(pReferencePoint[1]))
        elif len(pReferencePoint) == 3:
            view_point_start, view_point_end = self.hicMatrix.getRegionBinRange(pReferencePoint[0], int(pReferencePoint[1]), int(pReferencePoint[2]))
        else:
            log.error("No valid reference point given. {}".format(pReferencePoint))
            exit(1)
        return view_point_start, view_point_end

    def smoothInteractionValues(self, pData, pWindowSize):

        window_size = np.int(math.floor(pWindowSize / 2))
        window_size_upstream = window_size
        if pWindowSize % 2 == 0:
            window_size_upstream -= 1

        interactions = np.swapaxes(pData, 0, 1)[6].astype(float)
        average_contacts = np.zeros(len(pData))

        # add upstream and downstream, handle regular case
        for i in range(window_size_upstream, len(interactions) - window_size):
            start = i - window_size_upstream
            end = i + window_size + 1
            average_contacts_[i] = np.mean(interactions[start:end])
        
        # handle border conditions
        for i in range(window_size):
            start = i - window_size_upstream
            if start < 0:
                start = 0
            end = i + window_size + 1
        
            average_contacts[i] = np.mean(interactions[start:end])
            average_contacts[-(i + 1)] = np.mean(interactions[-end:])
        return average_contacts

    def calculateViewpointRange(self, pViewpoint, pRange):
        max_length = self.hicMatrix.getBinPos(self.hicMatrix.getChrBinRange(viewpoint[0])[1]-1)[2]
        region_start = int(viewpoint[1]) - pRange[0]
        if region_start < 0:
            region_start = 0
        log.debug('region_start {}'.format(region_start))

        region_end = int(viewpoint[2]) + pRange[1]
        if region_end > max_length:
            region_end = max_length
        log.debug('region_end {}'.format(region_end))
        
        return region_start, region_end 
    
    def createXlabels(self, pHeader):

        if len(referencePoint) == 2:
   
            ax.set_xticks([0, view_point_start - view_point_range[0], view_point_range[1] - view_point_range[0]])
            xticklabels = [None] * 3
            xticklabels[0] = relabelTicks((int(referencePoint[1]) - region_start) * (-1))
            xticklabels[1] = referencePoint[0] + ":" + relabelTicks(int(referencePoint[1]))
            xticklabels[2] = relabelTicks(region_end - int(referencePoint[1]))

        elif len(referencePoint) == 3:
            log.debug("Range mode: {}".format(referencePoint))

            # fit scale: start coordinate is 0 --> view_point_range[0]
            ax.set_xticks([0, view_point_start - view_point_range[0], view_point_end - view_point_range[0], view_point_range[1] - view_point_range[0]])
            xticklabels = [None] * 4
            xticklabels[0] = relabelTicks((int(referencePoint[1]) - region_start) * (-1))
            xticklabels[1] = referencePoint[0] + ":" + relabelTicks(int(referencePoint[1]))
            xticklabels[2] = referencePoint[0] + ":" + relabelTicks(int(referencePoint[2]))
            xticklabels[3] = relabelTicks(region_end - int(referencePoint[1]))
