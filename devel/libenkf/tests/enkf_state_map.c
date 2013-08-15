/*
   Copyright (C) 2013  Statoil ASA, Norway. 
    
   The file 'enkf_state_map.c' is part of ERT - Ensemble based Reservoir Tool. 
    
   ERT is free software: you can redistribute it and/or modify 
   it under the terms of the GNU General Public License as published by 
   the Free Software Foundation, either version 3 of the License, or 
   (at your option) any later version. 
    
   ERT is distributed in the hope that it will be useful, but WITHOUT ANY 
   WARRANTY; without even the implied warranty of MERCHANTABILITY or 
   FITNESS FOR A PARTICULAR PURPOSE.   
    
   See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html> 
   for more details. 
*/
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <unistd.h>

#include <ert/util/test_work_area.h>
#include <ert/util/test_util.h>
#include <ert/util/util.h>
#include <ert/util/thread_pool.h>
#include <ert/util/arg_pack.h>

#include <ert/enkf/state_map.h>
#include <ert/enkf/enkf_types.h>


void create_test() {
  state_map_type * state_map = state_map_alloc();
  test_assert_true( state_map_is_instance( state_map ));
  test_assert_int_equal( 0 , state_map_get_size( state_map ));
  state_map_free( state_map );
}

void get_test( ) {
  state_map_type * state_map = state_map_alloc();
  test_assert_int_equal( STATE_UNDEFINED , state_map_iget( state_map , 0 ));
  test_assert_int_equal( STATE_UNDEFINED , state_map_iget( state_map , 100 ));
  state_map_free( state_map );
}

void set_test( ) {
  state_map_type * state_map = state_map_alloc();
  state_map_iset( state_map , 0 , STATE_HAS_DATA );
  test_assert_int_equal( STATE_HAS_DATA , state_map_iget( state_map , 0 ));

  state_map_iset( state_map , 100 , STATE_HAS_DATA );
  test_assert_int_equal( STATE_HAS_DATA , state_map_iget( state_map , 100 ));

  test_assert_int_equal( STATE_UNDEFINED , state_map_iget( state_map , 50 ));
  test_assert_int_equal( 101 , state_map_get_size( state_map ));
  state_map_free( state_map );
}


void load_empty_test() {
  state_map_type * state_map = state_map_fread_alloc( "File/does/not/exists" );
  test_assert_true( state_map_is_instance( state_map ));
  test_assert_int_equal( 0 , state_map_get_size( state_map ));
  state_map_free( state_map );
}


void test_copy() {
  state_map_type * state_map = state_map_alloc();
  state_map_iset( state_map , 0 , STATE_HAS_DATA );
  state_map_iset( state_map , 100 , STATE_HAS_DATA );
  {
    state_map_type * copy = state_map_alloc_copy( state_map );
    test_assert_int_equal( state_map_get_size( copy ) , state_map_get_size( state_map ));

    for (int i=0; i < state_map_get_size( copy ); i++)
      test_assert_int_equal( state_map_iget( copy ,i ) , state_map_iget(state_map , i ));

    test_assert_true( state_map_equal( copy , state_map ));
    state_map_iset( state_map , 10 , STATE_HAS_DATA );
    test_assert_false( state_map_equal( copy , state_map ));                      

    state_map_free( copy );
  }
  state_map_free( state_map );
}


void test_io( ) {
  test_work_area_type * work_area = test_work_area_alloc( "enkf-state-map" , false );
  {
    state_map_type * state_map = state_map_alloc();
    state_map_type * copy;
    state_map_iset( state_map , 0 , STATE_HAS_DATA );
    state_map_iset( state_map , 100 , STATE_HAS_DATA );
    state_map_fwrite( state_map , "map");
    
    copy = state_map_fread_alloc( "map" );
    test_assert_true( state_map_equal( state_map , copy ));
  }
  test_work_area_free( work_area );
}



int main(int argc , char ** argv) {
  create_test();
  get_test();
  set_test();
  load_empty_test();
  test_copy();
  test_io();
  exit(0);
}

