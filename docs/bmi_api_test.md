<h2>BMI API test</h2>

<table>
  <tbody>
    <tr>
      <th>Ceph API</th>
      <th align="center">Arguments</th>
      <th align="right">Comments</th>
    </tr>
    <tr>
      <td>open_images</td>
      <td align="">img_id, img_size</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>list_images</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
    <tr>
      <td>create_image</td>
      <td align="">img_id, img_size</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>clone</td>
      <td align="">parent_img_name, parent_snap_name, clone_img_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>remove</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>write</td>
      <td align="">img_id, data, offset</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>snap_image</td>
      <td align="">img_id, name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>snap_protect</td>
      <td align="">img_id, snap_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>snap_unprotect</td>
      <td align="">img_id, snap_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>flatten</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>list_snapshots</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>remove_snapshot</td>
      <td align="">img_id, name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>get_image</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>get_parent_info</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>map</td>
      <td align="">ceph_img_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>unmap</td>
      <td align="">rbd_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>showmapped</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
    
    <!--<tr>
      <td>
        <ul>
          <li>item1</li>
          <li>item2</li>
        </ul>
      </td>
      <td align=""></td>
      <td align=""></td>
    </tr>-->
  </tbody>
</table>
