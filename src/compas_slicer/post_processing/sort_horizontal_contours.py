# from compas_slicer.geometry import VerticalLayersManager
import logging

logger = logging.getLogger('logger')

__all__ = ['sort_horizontal_contours']


def sort_horizontal_contours(slicer, dist_threshold=25.0, max_paths_per_layer=None):
    """Sorts the paths within a horizontal layer for an optimised toolpath, minimising total travel distances.

      Parameters
    ----------
    slicer: :class:`compas_slicer.slicers.BaseSlicer`
        An instance of one of the compas_slicer.slicers classes.
    dist_threshold: float
        The maximum get_distance that the centroids of two successive paths can have to belong in the same VerticalLayer
        Recommended value, slightly bigger than the layer height
    max_paths_per_layer: int
        Maximum number of layers that a vertical layer can consist of.
        If None, then the vertical layer has an unlimited number of layers.
    """
    logger.info("Sorting contours ...")

""" Dim myNewList As  New List (Of Curve)
    Dim myTempA, myTempB, myMin As Double
    Dim myIndex, i, myB As New Integer
    Dim myTempC As Curve
    Dim myTempPt As New Point3d

    For myB = 0 To myCurves.BranchCount - 1

      If myCurves.Branch(myB).Count > 0 Then

        'add first curve
        If myB = 0 Then
          myNewList.Add(myCurves.Branch(myB)(0))
          myCurves.Branch(myB).RemoveAt(0)
        Else'add first curve according to previous layer
          'find min distance to start with
          myIndex = 0
          myTempPt = myNewList(myNewList.Count - 1).PointAtEnd
          subAdjustSeam(myCurves.Branch(myB)(0), myTempPt, myBedSize)
          '
          myTempA = myTempPt.DistanceTo(myCurves.Branch(myB)(0).PointAtStart)
          myTempB = myTempPt.DistanceTo(myCurves.Branch(myB)(0).PointAtEnd)
          myTempC = myCurves.Branch(myB)(0)
          If myTempA < myTempB Then
            myMin = myTempA
          Else
            myMin = myTempB
            myTempC.Reverse
          End If

          For i = 1 To myCurves.Branch(myB).Count - 1
            myTempPt = myNewList(myNewList.Count - 1).PointAtEnd
            subAdjustSeam(myCurves.Branch(myB)(i), myTempPt, myMin)
            '
            myTempA = myTempPt.DistanceTo(myCurves.Branch(myB)(i).PointAtStart)
            myTempB = myTempPt.DistanceTo(myCurves.Branch(myB)(i).PointAtEnd)
            If myTempA < myTempB Then
              If myTempA < myMin Then
                myMin = myTempA
                myTempC = myCurves.Branch(myB)(i)
                myIndex = i
              End If
            Else If myTempB < myMin Then
              myMin = myTempB
              myTempC = myCurves.Branch(myB)(i)
              myTempC.Reverse
              myIndex = i
            End If
          Next
          myNewList.Add(myTempC)
          myCurves.Branch(myB).RemoveAt(myIndex)
          'If myIndex <> 0 Then
          '  myCurves.Branch(myB).Add(myCurves.Branch(myB)(0))
          'End If
        End If

        If myCurves.Branch(myB).Count > 0 Then

          While myCurves.Branch(myB).Count > 1

            myIndex = 0

            'find min distance to start with
            myTempPt = myNewList(myNewList.Count - 1).PointAtEnd
            subAdjustSeam(myCurves.Branch(myB)(0), myTempPt, myBedSize)
            '
            myTempA = myTempPt.DistanceTo(myCurves.Branch(myB)(0).PointAtStart)
            myTempB = myTempPt.DistanceTo(myCurves.Branch(myB)(0).PointAtEnd)
            myTempC = myCurves.Branch(myB)(0)
            If myTempA < myTempB Then
              myMin = myTempA
            Else
              myMin = myTempB
              myTempC.Reverse
            End If

            'loop all curves in myCurves
            For i = 1 To myCurves.Branch(myB).Count - 1
              myTempPt = myNewList(myNewList.Count - 1).PointAtEnd
              subAdjustSeam(myCurves.Branch(myB)(i), myTempPt, myMin)
              '
              myTempA = myTempPt.DistanceTo(myCurves.Branch(myB)(i).PointAtStart)
              myTempB = myTempPt.DistanceTo(myCurves.Branch(myB)(i).PointAtEnd)
              If myTempA < myTempB Then
                If myTempA < myMin Then
                  myMin = myTempA
                  myTempC = myCurves.Branch(myB)(i)
                  myIndex = i
                End If
              Else If myTempB < myMin Then
                myMin = myTempB
                myTempC = myCurves.Branch(myB)(i)
                myTempC.Reverse
                myIndex = i
              End If
            Next

            myNewList.Add(myTempC)
            myCurves.Branch(myB).RemoveAt(myIndex)

          End While

          'add the last curve
          myTempPt = myNewList(myNewList.Count - 1).PointAtEnd
          subAdjustSeam(myCurves.Branch(myB)(0), myTempPt, myBedSize)
          '
          myTempA = myTempPt.DistanceTo(myCurves.Branch(myB)(0).PointAtStart)
          myTempB = myTempPt.DistanceTo(myCurves.Branch(myB)(0).PointAtEnd)
          'myTempC = myCurves.Branch(myB)(0)
          If myTempA > myTempB Then
            myCurves.Branch(myB)(0).Reverse
          End If
          myNewList.Add(myCurves.Branch(myB)(0))
        End If
      End If

    Next

    A = myNewList
"""