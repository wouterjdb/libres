import unittest
from ecl.test import ExtendedTestCase, TestAreaContext
from res.test import ErtTestContext

from res.enkf import RunpathList, RunpathNode, ErtRunContext
from res.enkf.enums import EnkfInitModeEnum,EnkfRunType
from ecl.util import BoolVector
from res.util.substitution_list import SubstitutionList




def path(idx):
    return 'path_%d' % idx

def base(idx):
    return 'base_%d' % idx

class RunpathListTest(ExtendedTestCase):

    def test_an_enkf_runpath(self):
        # TODO this test is flaky and we need to figure out why.  See #1370
        # enkf_util_assert_buffer_type: wrong target type in file (expected:104 got:0)
        test_path = self.createTestPath("local/snake_oil_field/snake_oil.ert")
        with ErtTestContext("runpathlist_basic", test_path) as tc:
            pass

    def test_runpath_list(self):
        runpath_list = RunpathList('')

        self.assertEqual(len(runpath_list), 0)

        test_runpath_nodes = [RunpathNode(0, 0, "runpath0", "basename0"), RunpathNode(1, 0, "runpath1", "basename0")]

        runpath_node = test_runpath_nodes[0]
        runpath_list.add(runpath_node.realization, runpath_node.iteration, runpath_node.runpath, runpath_node.basename)

        self.assertEqual(len(runpath_list), 1)
        self.assertEqual(runpath_list[0], test_runpath_nodes[0])

        runpath_node = test_runpath_nodes[1]
        runpath_list.add(runpath_node.realization, runpath_node.iteration, runpath_node.runpath, runpath_node.basename)

        self.assertEqual(len(runpath_list), 2)
        self.assertEqual(runpath_list[1], test_runpath_nodes[1])

        for index, runpath_node in enumerate(runpath_list):
            self.assertEqual(runpath_node, test_runpath_nodes[index])


        runpath_list.clear()

        self.assertEqual(len(runpath_list), 0)


    def test_collection(self):
        """Testing len, adding, getting (idx and slice), printing, clearing."""
        with TestAreaContext("runpath_list_collection"):
            runpath_list = RunpathList("EXPORT.txt")
            runpath_list.add( 3 , 1 , path(3) , base(3) )
            runpath_list.add( 1 , 1 , path(1) , base(1) )
            runpath_list.add( 2 , 1 , path(2) , base(2) )
            runpath_list.add( 0 , 0 , path(0) , base(0) )
            runpath_list.add( 3 , 0 , path(3) , base(3) )
            runpath_list.add( 1 , 0 , path(1) , base(1) )
            runpath_list.add( 2 , 0 , path(2) , base(2) )
            runpath_list.add( 0 , 1 , path(0) , base(0) )

            self.assertEqual(8, len(runpath_list))
            pfx = 'RunpathList(size' # the __repr__ function
            self.assertEqual(pfx, repr(runpath_list)[:len(pfx)])
            node2 = RunpathNode(2, 1 , path(2), base(2))
            self.assertEqual(node2, runpath_list[2])

            node3 = RunpathNode(0,0,path(0),base(0))
            node4 = RunpathNode(3,0,path(3),base(3))
            node5 = RunpathNode(1,0,path(1),base(1))
            node6 = RunpathNode(2,0,path(2),base(2))
            nodeslice = [node3, node4, node5, node6]
            self.assertEqual(nodeslice, runpath_list[3:7])
            self.assertEqual(node6, runpath_list[-2])
            with self.assertRaises(TypeError):
                runpath_list["key"]
            with self.assertRaises(IndexError):
                runpath_list[12]

            runpath_list.clear()
            self.assertEqual(0, len(runpath_list))
            with self.assertRaises(IndexError):
                runpath_list[0]
            self.assertEqual('EXPORT.txt', runpath_list.getExportFile())


    def test_sorted_export(self):
        with TestAreaContext("runpath_list_sorted"):
            runpath_list = RunpathList("EXPORT.txt")
            runpath_list.add( 3 , 1 , "path" , "base" )
            runpath_list.add( 1 , 1 , "path" , "base" )
            runpath_list.add( 2 , 1 , "path" , "base" )
            runpath_list.add( 0 , 0 , "path" , "base" )

            runpath_list.add( 3 , 0 , "path" , "base" )
            runpath_list.add( 1 , 0 , "path" , "base" )
            runpath_list.add( 2 , 0 , "path" , "base" )
            runpath_list.add( 0 , 1 , "path" , "base" )

            runpath_list.export( )

            path_list = []
            with open("EXPORT.txt") as f:
              for line in f.readlines():
                    tmp = line.split()
                    iens = int(tmp[0])
                    iteration = int(tmp[3])

                    path_list.append( (iens , iteration) )

            for iens in range(4):
                t0 = path_list[iens]
                t4 = path_list[iens + 4]
                self.assertEqual( t0[0] , iens )
                self.assertEqual( t4[0] , iens )

                self.assertEqual( t0[1] , 0 )
                self.assertEqual( t4[1] , 1 )


    def test_assert_export(self):
        with ErtTestContext("create_runpath_export" , self.createTestPath("local/snake_oil_no_data/snake_oil.ert")) as tc:
            ert = tc.getErt( )
            runpath_list = ert.getRunpathList( )
            self.assertFalse( os.path.isfile( runpath_list.getExportFile( ) ))

            ens_size = ert.getEnsembleSize( )
            runner = ert.getEnkfSimulationRunner( )
            fs_manager = ert.getEnkfFsManager( )

            init_fs = fs_manager.getFileSystem("init_fs")
            mask = BoolVector( initial_size = 25 , default_value = True )
            runpath_fmt = ert.getModelConfig().getRunpathFormat( )
            subst_list = SubstitutionList( )
            itr = 0
            jobname_fmt = ert.getModelConfig().getJobnameFormat()
            run_context1 = ErtRunContext( EnkfRunType.INIT_ONLY , init_fs, None , mask , runpath_fmt, jobname_fmt, subst_list , itr )

            runner.createRunPath( run_context1 )

            self.assertTrue( os.path.isfile( runpath_list.getExportFile( ) ))
            self.assertEqual( "test_runpath_list.txt" , os.path.basename( runpath_list.getExportFile( ) ))


    def test_assert_symlink_deleted(self):
        with ErtTestContext("create_runpath_symlink_deleted" , self.createTestPath("local/snake_oil_field/snake_oil.ert")) as tc:
            ert = tc.getErt( )
            runpath_list = ert.getRunpathList( )

            ens_size = ert.getEnsembleSize()
            runner = ert.getEnkfSimulationRunner()
            mask = BoolVector( initial_size = ens_size , default_value = True )
            fs_manager = ert.getEnkfFsManager()
            init_fs = fs_manager.getFileSystem("init_fs")

            # create directory structure
            runpath_fmt = ert.getModelConfig().getRunpathFormat( )
            subst_list = SubstitutionList( )
            itr = 0
            jobname_fmt = ert.getModelConfig().getJobnameFormat()
            run_context = ErtRunContext( EnkfRunType.INIT_ONLY , init_fs, None , mask , runpath_fmt, jobname_fmt, subst_list , itr )
            runner.createRunPath( run_context )


            # replace field file with symlink
            linkpath = '%s/permx.grdcel' % str(runpath_list[0].runpath)
            targetpath = '%s/permx.grdcel.target' % str(runpath_list[0].runpath)
            open(targetpath, 'a').close()
            os.remove(linkpath)
            os.symlink(targetpath, linkpath)

            # recreate directory structure
            runner.createRunPath( run_context )

            # ensure field symlink is replaced by file
            self.assertFalse( os.path.islink(linkpath) )


